import json
import requests
import threading

from flask_socketio import SocketIO, emit
from flask import request
from .dispatch_handler import dispatch_handler

from .diff_synch import *
from services.models import *

class synch_server:
    def __init__(self, app, db, own_id, own_url, replicas, dispatcher_url, logging=True):
        self.app = app
        self.db = db
        self.own_id = own_id
        self.own_url = own_url
        self.replicas = replicas
        self.logging = logging
        self.socket = SocketIO(app, cors_allowed_origins="*")
        self.dispatcher = dispatch_handler(dispatcher_url)
        self.client_sockets = {}
        self.clients_of_file = {}
        self.setup()
    
    def run(self, *args, **kwargs):
        self.socket.run(self.app, *args, **kwargs)
    
    def create_new_file(self, file_id, text="", create_reps=False, add_replica=None):
        if File.hasId(file_id):
            self.log("Tried creating a new file with id " + file_id + " but it was created before", level="ERROR")
        
        self.log("Creating new file with id: " + file_id)
        File.insert(file_id, text)
        self.dispatcher.notify(file_id, self.own_id, self.own_url)
        if create_reps:
          threading.Thread(target=self.create_replicas, args=(file_id,)).start()
        else:
          if not add_replica is None:
              self.replicas.add_replica(file_id, *add_replica)
        self.log("Finished creating new file with id: " + file_id)

    def setup(self):
        @self.socket.on('req_text')
        def req_text(msg):
            socket_id = request.sid
            msg = json.loads(msg)
            file_id = msg["file_id"]
            conn_id = msg["conn_id"]
            if not File.hasId(file_id):
                self.create_new_file(file_id, create_reps=True)
                file_text = ""
            else:
                file_text = File.getById(file_id)
            if not socket_id in self.client_sockets.keys():
                if conn_id in self.replicas.get_replica_ids(file_id):  # a replica
                    self.client_sockets[socket_id] = [file_id, self.replicas.get_diff_synch(file_id, conn_id)]
                else:
                    self.client_sockets[socket_id] = [file_id, diff_synch(file_text)]
                    if not file_id in self.clients_of_file.keys():
                        self.clients_of_file[file_id] = []
                    self.clients_of_file[file_id].append(socket_id)
                    threading.Thread(target=self.replicas.connect, args=(file_id,)).start()
            emit("res_text", file_text)

        @self.socket.on('connect')
        def connect():
            socket_id = request.sid
            self.log("Connected a client with socket id: " + socket_id)

        @self.socket.on('disconnect')
        def disconnect():
            socket_id = request.sid
            self.log("Disconnecting a client with socket id: " + socket_id)
            if socket_id in self.client_sockets.keys():
                file_id = self.client_sockets[socket_id][0]
                if socket_id in self.clients_of_file[file_id]:
                    self.clients_of_file[file_id].remove(socket_id)
                    if len(self.clients_of_file[file_id]) == 0:
                        self.replicas.disconnect(file_id) 
                del self.client_sockets[socket_id]


        @self.socket.on('update')
        def update(msg):
            socket_id = request.sid
            updates = json.loads(msg)
            if socket_id in self.client_sockets.keys():
                file_id = self.client_sockets[socket_id][0]
                file_text = File.getById(file_id)
                new_text = self.client_sockets[socket_id][1].recieve_updates(*updates, file_text)
                File.editById(file_id, new_text)
                to_send = self.client_sockets[socket_id][1].send_updates(new_text)
                id = self.client_sockets[socket_id][1].server_id
                emit("res_update", json.dumps(to_send))
                if new_text != file_text:
                    #threading.Thread(target=self.replicas.update, args=(file_id, new_text, id, )).start()
                    self.replicas.update(file_id, new_text, id)

    def create_replicas(self, file_id, n_replicas_needed=2):
        replica_data = [[self.own_id, self.own_url]]
        while len(replica_data) < n_replicas_needed:
            servers = self.dispatcher.get_servers(n_replicas_needed-len(replica_data))
            for server_id, server_url in servers:
                if server_id != self.own_id:
                    response = requests.post(server_url+'/add_new_file',json={"file_id":file_id,"server_id":self.own_id,"server_url":self.own_url})
                    if response.status_code == 200:
                        replica_data.append([server_id, server_url])

        self.replicas.set_replicas(file_id, replica_data)
        with self.app.app_context():
            Replica.deleteById(file_id)
            for rep in replica_data:
                Replica.insert(file_id, *rep)
        for server_id, server_url in replica_data:
            if server_id != self.own_id:
                requests.post(server_url+'/update_replicas', json={'file_id':file_id, 'replicas':replica_data})
        self.replicas.update(file_id, "")
    
    def log(self, msg, level="INFO"):
        if self.logging:
            print(self.own_id + "," + level+": "+msg)
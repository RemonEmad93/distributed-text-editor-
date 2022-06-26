import json
import socketio

from .diff_synch import *

class synch_client:
    '''
    A client side synchronizer of a text file. It connects to a given server and synchronizes text across both sides

    Parameters
    ----------
    file_id: str
        The id of the text file
    server_id: str
        A unique id given to each server
    server_url: str
        A url (ip and port) used to connect a socket to that server
    edit_text_callback: a callable function that takes as input (file_id: str, new_text: str)
        It modifies the text file with given (file_id) to be the new text (new_text)
    get_text_callback: a callable function that takes as input (file_id: str)
        Returns the text file with given (file_id)
    text: str
        The value of the text file at creating this object
    '''
    def __init__(self, file_id, own_id, server_id, server_url, edit_text_callback, get_text_callback, text = ""):
        self.file_id = file_id
        self.server_id = server_id
        self.own_id = own_id
        self.server_url = server_url
        self.edit_text_callback = edit_text_callback
        self.get_text_callback = get_text_callback
        self.sio = None
        self.diff_synch = diff_synch(text, server_id)
        self.can_send = False
        self.reqs_to_send = None
        self.socket_id = None
    
    def connect(self):
        self.sio = socketio.Client()

        @self.sio.on("res_update")
        def update(data):
            self.can_send = False
            updates = json.loads(data)
            file_text = self.get_text_callback(self.file_id)
            new_text = self.diff_synch.recieve_updates(*updates, file_text)
            self.edit_text_callback(self.file_id, new_text)
            updates = self.diff_synch.send_updates(new_text)
            if len(updates[0])>1 or len(updates[0][0][0])>0: # There is an update to send
                self.sio.emit("update", json.dumps(updates))
            else:
                self.can_send = True

        @self.sio.on("res_text")
        def res_test(msg):
            self.diff_synch.shadow_text = msg
            self.diff_synch.backup_text = msg
            file_text = self.get_text_callback(self.file_id)
            updates = self.diff_synch.send_updates(file_text)
            self.sio.emit("update", json.dumps(updates))

        @self.sio.event
        def disconnect():
            self.sio = None

        @self.sio.event
        def connect():
            self.socket_id = self.sio.sid
            self.sio.emit("req_text",json.dumps({"file_id":self.file_id,"conn_id":self.own_id}))

        print("Connecting:", self.server_url)
        self.sio.connect(self.server_url)

    def update(self, new_text):
        '''
        Own text has changed, send edit stack to the other server

        Parameters
        ----------
        new_text: str
            The new changed text
        '''
        if self.sio is None:  # If the socket has started, start it
            self.connect()
        if self.can_send:
            updates = self.diff_synch.send_updates(new_text)
            self.sio.emit("update", json.dumps(updates))
        else:
            self.reqs_to_send = new_text
    
    def disconnect(self):
        if not self.sio is None:
            self.sio.disconnect()
            self.sio = None
        self.can_send = False
        self.socket_id = None
    def __repr__(self):
        own_str = "To: "+self.server_id+"\n"
        own_str += "State: "
        if self.sio is None:
            own_str += "Disconnected\n"
        else:
            own_str += "Connected\n"
        own_str += "URL:"+self.server_url+"\n"
        own_str += "SID:"+str(self.socket_id)+"\n"
        own_str += "Shadow text: "+self.diff_synch.shadow_text+"\n"
        own_str += "Backup text: "+self.diff_synch.backup_text+"\n"
        own_str += "Own version: "+str(self.diff_synch.own_version)+"\n"
        own_str += "Other version: "+str(self.diff_synch.other_version)+"\n"
        return own_str
from .synch_client import *

class replicas_handler:
    def __init__(self, own_id, edit_text, get_text, excluded_ids=[]):
        self.own_id = own_id
        self.edit_text = edit_text
        self.get_text = get_text
        self.file_replicas = {}
        self.excluded_ids = excluded_ids
    
    def add_replica(self, file_id, *args, **kwargs):
        self.check_has_file(file_id)
        self.file_replicas[file_id].add_replica(*args, **kwargs)

    def add_replicas(self, file_id, *args, **kwargs):
        self.check_has_file(file_id)
        self.file_replicas[file_id].add_replicas(*args, **kwargs)
    
    def set_replicas(self, file_id, *args, **kwargs):
        self.check_has_file(file_id)
        self.file_replicas[file_id].set_replicas(*args, **kwargs)
    
    def update(self, file_id, *args, **kwargs):
        self.check_has_file(file_id)
        self.file_replicas[file_id].update(*args, **kwargs)
    
    def connect(self, file_id, *args, **kwargs):
        self.check_has_file(file_id)
        self.file_replicas[file_id].connect(*args, **kwargs)
    
    def check_has_file(self, file_id):
        if not file_id in self.file_replicas.keys():
            self.file_replicas[file_id] = file_replica_handler(file_id, self.own_id, self.edit_text, self.get_text, self.excluded_ids)
    
    def get_sids(self, file_id):
        self.check_has_file(file_id)
        return self.file_replicas[file_id].get_sids()
    
    def get_replica_ids(self, file_id):
        '''
        Returns server_id for all replicas of file_id
        '''
        self.check_has_file(file_id)
        return self.file_replicas[file_id].server_ids
    
    def get_diff_synch(self, file_id, server_id):
        self.check_has_file(file_id)
        return self.file_replicas[file_id].get_diff_synch(server_id)

    def disconnect(self, file_id):
        self.check_has_file(file_id)
        self.file_replicas[file_id].disconnect()
        
    def __repr__(self):
        own_str = "{"
        for key in self.file_replicas.keys():
            own_str += key + ": \n" + str(self.file_replicas) + ",\n\n"
        own_str += "}"
        return own_str


class file_replica_handler:
    def __init__(self, file_id, own_id, edit_text, get_text, excluded_ids=[]):
        self.edit_text = edit_text
        self.get_text = get_text
        self.file_id = file_id
        self.own_id = own_id
        self.replicas = []
        self.server_ids = []
        self.excluded_ids = excluded_ids

    def add_replica(self, server_id, server_url, text=""):
        if not server_id in self.server_ids and not server_id in self.excluded_ids:
            self.replicas.append(synch_client(self.file_id, self.own_id, server_id, server_url, self.edit_text, self.get_text, text=text))
            self.server_ids.append(server_id)
    
    def add_replicas(self, servers, text=""):
        for server_id, server_url in servers:
            self.add_replica(server_id, server_url, text=text)
        
    def set_replicas(self, servers, text=""):
        for rep in self.replicas:
            rep.disconnect()
        self.replicas = []
        self.server_ids = []
        self.add_replicas(servers,text=text)
    
    def update(self, new_text, ignore_id=None):
        for rep in self.replicas:
            if rep.diff_synch.server_id != ignore_id:
                rep.update(new_text)
    
    def get_sids(self):
        socket_ids = []
        for rep in self.replicas:
            if not rep.socket_id is None:
                socket_ids.append(rep.socket_id)
        return socket_ids
    
    def get_by_sid(self, socket_id):
        for rep in self.replicas:
            if rep.socket_id == socket_id:
                return rep
        return None
    
    def get_diff_synch(self, server_id):
        if server_id in self.server_ids:
            for rep in self.replicas:
                if rep.server_id == server_id:
                    return rep.diff_synch
        return None
    
    def connect(self):
        for rep in self.replicas:
            if rep.sio is None:
                rep.connect()
    def disconnect(self):
        for rep in self.replicas:
            rep.disconnect()
    
    def __repr__(self):
        own_str = "File id: "+self.file_id + "\n"
        own_str += "From: "+str(self.excluded_ids)+"\n"
        own_str += "Server ids: "+str(self.server_ids) + "\n"
        own_str += "Replicas: "+str(self.replicas)
        return own_str
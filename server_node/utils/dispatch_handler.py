import requests
import json

class dispatch_handler:
    def __init__(self, dispatcher_url):
        self.dispatcher_url = dispatcher_url
    
    def get_servers(self, n=2):
        resp = requests.post(self.dispatcher_url+"/get_servers")
        resp = json.loads(resp.text)
        return resp

    def notify(self, file_id, server_id, server_url):
        requests.post(self.dispatcher_url+"/notify", json={"file_id":file_id, "server_id":server_id, "server_url":server_url})
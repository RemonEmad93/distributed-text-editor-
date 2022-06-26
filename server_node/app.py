import sys

from flask_cors import CORS
from flask import Flask, render_template, request

from utils.synch_client import *
from utils.synch_server import *
from utils.replica_handler import *
from services.models import db, File

INIT_DB = True  
own_id = sys.argv[1]
host = sys.argv[2]
port = sys.argv[3]
own_url = host+":"+port
DB_FILENAME = 'files_db'+own_id+'.db'

def create_app():
    # create flask app
    app = Flask(__name__)

    # create database extension
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_FILENAME
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY']='41e856c5d1833e5d9836c355e738135e'
    db.init_app(app)

    # create flask cors extension
    CORS(app)
    
    if INIT_DB:
        db.create_all(app=app)

    def get_file(file_id):
        with app.app_context():
            return File.getById(file_id)
    def edit_file(file_id, text=""):
        with app.app_context():
            File.editById(file_id, text)
    with app.app_context():
        replicas_in_db = Replica.getAll()
        replicas = replicas_handler(own_id, edit_file, get_file, excluded_ids=[own_id])
        for rep in replicas_in_db:
            file_text = ""
            if File.hasId(rep[0]):
                file_text = File.getById(rep[0])
            else:
                pass
            replicas.add_replica(*rep, text=file_text)
    # Load saved replicas
    server = synch_server(app, db, own_id, own_url, replicas, "http://localhost:3000")

    return app, server


app, server = create_app()
from consts import rand_num
@app.route('/')
def test():
    return render_template('test.html', data={'temp_id':str(rand_num)})

@app.route('/admin')
def admin_view():
    return render_template('admin.html', data={'replicas':str(server.replicas).replace('\n','<br/>'),'clients':str(server.client_sockets),'client_files':str(server.clients_of_file)})

@app.route('/add_new_file', methods=["POST"])
def add_new_file():
    file_id = request.json["file_id"]
    server_id = request.json["server_id"]
    server_url = request.json["server_url"]

    if File.hasId(file_id):
        print("Error: Requested to create a file that is already available")  # shouldn't happen, raise error in server

    server.create_new_file(file_id, add_replica=[server_id, server_url])
    Replica.insert(file_id, server_id, server_url)
    return "Success", 200

@app.route('/update_replicas', methods=["POST"])
def update_replicas():
    file_id = request.json["file_id"]
    replicas_data = request.json["replicas"]
    server.replicas.set_replicas(file_id, replicas_data)
    Replica.deleteById(file_id)
    for rep in replicas_data:
        Replica.insert(file_id, *rep)
    return "Success", 200

def crash2():
    x = []
    x[10] = 5
@app.route('/crash')
def crash():
    crash2()
if __name__ == '__main__':
    server.run(debug=True, port=port, log_output=False)

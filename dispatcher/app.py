from flask import Flask, render_template, redirect, flash, session, request
from flask_cors import CORS
from services.models import db, User, File, Server
from forms.login import loginForm
from forms.register import registerForm
import random
import json

##### CONSTANTS #####
PORT = 3000
DB_FILENAME = 'dbfile.db'
INIT_DB = True  


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

    return app, db

app, db = create_app()

# create db file on demand
if INIT_DB:
    db.create_all(app=app)

with app.app_context():
    if not User.hasUsername("sawah"):
        User.insert("sawah","sawah@sawah.com","123456")

class Dispatcher:
    def __init__(self):
        self.client_idx = 0
        self.file_idx = 0
        self.servers = [["0","http://localhost:5000"],["1","http://localhost:5001"]]
    
    def get_client_servers(self, n):
        servs = []
        while len(servs)<n:
            servs.append(self.servers[self.client_idx])
            self.client_idx = (self.client_idx+1)%len(self.servers)
        return servs

    def get_file_servers(self, n):
        servs = []
        while len(servs)<n:
            servs.append(self.servers[self.file_idx])
            self.file_idx = (self.file_idx+1)%len(self.servers)
        return servs

dispatcher = Dispatcher()
#####################  routes  #####################

#####  main route  #####
@app.route('/', methods=['GET','POST'])
def login():
    form=loginForm()
    if form.validate_on_submit():

        # default admin email and password 
        if form.email.data== "admin" and form.password.data== "admin":
            flash(f' login successfully !', 'success')
            return redirect('/admin')

        try:
           user= User.getByEmail(email=form.email.data)
        except:
            flash(f'Error: Please login again !', 'danger')
            return redirect("/")
        
        # check user entered data
        if user==None or user.password != form.password.data:
            flash(f' Wrong data entered !', 'danger')
            return redirect("/")
        else:
            session.permanent = True
            # session['email'] = form.email.data
            session['name']= User.getByEmail(form.email.data).username
            flash(f' login successfully !', 'success')
            return redirect('/user')

    return render_template('userLogin.html',form=form)


#####  signUp route  #####
@app.route('/signUp', methods=['GET','POST'])
def signUp():
    form = registerForm()
    if form.validate_on_submit():
        try:
            User.insert(username=form.name.data, email=form.email.data, password=form.password.data)
        except:
            flash(f'Error: Please register again !', 'danger')
            return redirect("/signUp")
        
        flash(f'Account created for {form.name.data} !', 'success')
        return redirect('/')

    return render_template('registration.html', form=form)


#####  admin route  #####
@app.route('/admin')
def get_admin():

    return render_template('admin.html')


#####  user route  #####
@app.route('/user')
def get_user():
    files = File.getByUsername(session["name"])
    return render_template('userLanding.html', username=session['name'], files=files)


#####  logout  #####
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/create_file', methods=["POST"])
def create_file():
    file_id = "f"+str(random.random())[2:]
    filename = request.form.getlist('newFile')[0]
    print(file_id)
    File.insert(session["name"],filename, file_id)
    server = dispatcher.get_file_servers(1)[0]
    return render_template("userTextFile.html", username=session["name"], filename=filename, server_id=server[0], server_url=server[1], file_id=file_id)

@app.route('/open_file', methods=["POST"])
def open_file():
    filename = request.form.getlist("recentFile")[0]
    file_id=File.getByFilename(filename).file_id
    servers = Server.getById(file_id)
    server = dispatcher.get_client_servers(1)[0]
    return render_template("userTextFile.html", username=session["name"], filename=filename, server_id=server[0], server_url=server[1], file_id=file_id)

@app.route('/add_file', methods=["POST"])
def add_file():
    filename = request.form.getlist("joinFile")[0]
    file_id=File.getByFilename(filename).file_id
    if File.hasId(file_id):
        File.insert(session["name"], filename, file_id)
        servers = Server.getById(file_id)  # can cause bugs
        server = servers[random.randint(0,len(servers)-1)]
        return render_template("userTextFile.html", username=session["name"], filename=filename, server_id=server[0], server_url=server[1], file_id=file_id)
    return "File not found"

@app.route('/notify', methods=["POST"])
def notify():
    file_id = request.json["file_id"]
    server_id = request.json["server_id"]
    server_url = request.json["server_url"]
    Server.insert(file_id, server_id, server_url)

    return "Success", 200

@app.route('/get_servers', methods=["POST"])
def get_servers_route():
    return json.dumps(dispatcher.get_file_servers(2))

#####  404 page  #####
@app.errorhandler(404)
def error_404(e):
    return render_template("404.html"),404



if __name__ == '__main__':
    app.run(debug=True, port=PORT)
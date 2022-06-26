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
#####  404 page  #####
@app.errorhandler(404)
def error_404(e):
    return render_template("404.html"),404



if __name__ == '__main__':
    app.run(debug=True, port=PORT)
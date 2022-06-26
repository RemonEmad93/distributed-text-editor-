from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fileinput import filename

db = SQLAlchemy()

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True, nullable=False)
    username=db.Column(db.String(100), nullable=False )
    email=db.Column(db.String(100), unique=True, nullable=False)
    password=db.Column(db.String(100), nullable=False)
    created_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def __init__(self, username, email, password):
        self.username= username
        self.email = email
        self.password = password
    def __repr__(self):
        return f"<User({self.id}, {self.username}, {self.email}, {self.password}>"

    @classmethod
    def insert(self, username, email, password):

        user = User(username=username, email=email, password=password)

        db.session.add(user)
        db.session.commit()
    
    @classmethod
    def getByEmail(self, email):

        query = self.query.filter_by(email=email).first()
        return query
    @classmethod
    def hasUsername(self, username):
        query = self.query.filter_by(username=username)
        return query.count()>0

class File(db.Model):
    id=db.Column(db.Integer, primary_key=True, nullable=False)
    username=db.Column(db.String(100), nullable=False ) 
    filename=db.Column(db.String(100), nullable=False )
    file_id=db.Column(db.String(100), nullable=False)


    def __init__(self, username, filename, file_id):
        self.username= username
        self.filename= filename
        self.file_id = file_id

    def __repr__(self):
        return f"<File({self.id}, {self.username}, {self.filename}, {self.file_id}>"

    @classmethod
    def insert(self, username, filename, file_id):

        file = File(username=username, filename=filename, file_id=file_id)

        db.session.add(file)
        db.session.commit()
    
    @classmethod
    def getByUsername(self, username):
        query = self.query.filter_by(username=username).all()
        file_ids = [q.filename for q in query]
        return file_ids
    
    @classmethod
    def getByFileID(self, file_id):
        query = self.query.filter_by(file_id=file_id).first()
        return query
    @classmethod
    def getByFilename(self, filename):
        query = self.query.filter_by(filename=filename).first()
        return query


    @classmethod
    def hasId(self, file_id):
        query = self.query.filter_by(file_id=file_id)
        return query.count()>0


class Server(db.Model):
    id=db.Column(db.Integer, primary_key=True, nullable=False)
    file_id=db.Column(db.String(100), nullable=False)
    server_id=db.Column(db.String(100), nullable=False )
    server_url=db.Column(db.String(100), nullable=False )


    def __init__(self, file_id, server_id, server_url):
        self.file_id = file_id
        self.server_id = server_id
        self.server_url = server_url

    def __repr__(self):
        return f"<Server({self.id}, {self.file_id}, {self.server_id}, {self.server_url}>"

    @classmethod
    def insert(self, file_id, server_id, server_url):

        server = Server(file_id=file_id, server_id=server_id, server_url=server_url)

        db.session.add(server)
        db.session.commit()
    
    @classmethod
    def getById(self, file_id):
        query = self.query.filter_by(file_id=file_id).all()
        server_data = [[q.server_id, q.server_url] for q in query]
        return server_data
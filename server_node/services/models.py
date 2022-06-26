from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    file_id=db.Column(db.String(30), nullable=False)
    text=db.Column(db.String(1000), nullable=False )

    def __init__(self, file_id, text=""):
        self.file_id = file_id
        self.text = text

    def __repr__(self):
        return f"<File({self.file_id}, {self.text})>"

    @classmethod
    def insert(self, file_id, text=""):

        file = File(file_id, text)

        db.session.add(file)
        db.session.commit()
    
    @classmethod
    def hasId(self, file_id):
        query = self.query.filter_by(file_id=file_id)
        return query.count()>0
    
    @classmethod
    def getById(self, file_id):
        query = self.query.filter_by(file_id=file_id).first()
        return query.text
    
    @classmethod
    def editById(self, file_id, new_text):
        query = self.query.filter_by(file_id=file_id).first()
        query.text = new_text
        db.session.commit()
    
    @classmethod
    def getAllData(self):
        return ""


class Replica(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    file_id=db.Column(db.String(30), nullable=False)
    server_id=db.Column(db.String(100), nullable=False )
    server_url=db.Column(db.String(100), nullable=False )

    def __init__(self, file_id, server_id, server_url):
        self.file_id = file_id
        self.server_id = server_id
        self.server_url = server_url

    def __repr__(self):
        return f"<Replica({self.file_id}, {self.server_id}, {self.server_url})>"

    @classmethod
    def insert(self, file_id, server_id, server_url):

        replica = Replica(file_id, server_id, server_url)

        db.session.add(replica)
        db.session.commit()
    
    @classmethod
    def hasId(self, file_id):
        query = self.query.filter_by(file_id=file_id)
        return query.count()>0
    
    @classmethod
    def getById(self, file_id):
        query = self.query.filter_by(file_id=file_id).all()
        replicas = []
        for rep in query:
            replicas.append([rep.file_id, rep.server_id, rep.server_url])
        return replicas
    @classmethod
    def deleteById(self, file_id):
        query = self.query.filter_by(file_id=file_id).all()
        for q in query:
            db.session.delete(q)
        db.session.commit()
    @classmethod
    def getAll(self):
        query = self.query.filter_by().all()
        replicas = []
        for rep in query:
            replicas.append([rep.file_id, rep.server_id, rep.server_url])
        return replicas
    
    @classmethod
    def getAllData(self):
        return ""
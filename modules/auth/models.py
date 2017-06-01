#coding: utf8

'''
mappings applications et utilisateurs
'''

import hashlib
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    '''
    Représente un utilisateur
    '''
    __tablename__ = 'auth_utilisateur'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.Unicode(length=100))
    _password = db.Column('password', db.Unicode(length=100))
    nom = db.Column(db.Unicode(length=100))
    prenom = db.Column(db.Unicode(length=100))
    email = db.Column(db.Unicode(length=250))
    token = db.Column(db.Unicode(length=100))
    applications = db.relationship('AppUser', lazy='joined')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        self._password = hashlib.sha256(pwd.encode('utf8')).hexdigest()

    def check_password(self, pwd):
        return self._password == hashlib.sha256(pwd.encode('utf8')).hexdigest()

    def to_json(self):
        out = {
                'id': self.id,
                'login': self.login,
                'email': self.email,
                'nom': self.nom,
                'prenom': self.prenom,
                'applications': []
                }
        for app_data in self.applications:
            app = {
                    'id': app_data.application_id,
                    'nom': app_data.application.nom,
                    'niveau': app_data.niveau
                    }
            out['applications'].append(app)
        return out




class Application(db.Model):
    '''
    Représente une application ou un module
    '''
    __tablename__ = 'auth_application'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode(length=100))




class AppUser(db.Model):
    '''
    Relations entre applications et utilisateurs
    '''
    __tablename__ = 'auth_rel_app_user'
    user_id = db.Column(db.Integer,
            db.ForeignKey('auth_utilisateur.id'), primary_key=True)
    application_id = db.Column(db.Integer,
            db.ForeignKey('auth_application.id'), primary_key=True)
    niveau = db.Column(db.Integer)
    user = db.relationship('User',
            backref='relations', lazy='joined')
    application = db.relationship('Application',
            backref='relations', lazy='joined')

'''
mappings applications et utilisateurs
'''

import hashlib
import json
from server import db


class AuthStatus(db.Model):
    '''
    Informations de session utilisateur
    '''
    __tablename__ = 'auth_status'
    user_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Unicode(length=100))
    expiration = db.Column(db.Date)
    userdata = db.Column(db.UnicodeText)

    def as_dict(self):
        return {
            'id': self.user_id,
            'token': self.token,
            'userdata': json.loads(self.userdata)
        }


class User(db.Model):
    '''
    Représente un utilisateur
    '''
    __tablename__ = 'auth_utilisateur'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.Unicode(length=100))
    _password = db.Column('password', db.Unicode(length=100))
    name = db.Column(db.Unicode(length=100))
    email = db.Column(db.Unicode(length=250))
    groups = db.relationship(
        'Group',
        secondary='auth_rel_user_group',
        lazy='joined')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        self._password = hashlib.sha256(pwd.encode('utf8')).hexdigest()

    def check_password(self, pwd):
        return self._password == hashlib.sha256(pwd.encode('utf8')).hexdigest()

    def to_json(self):
        return {
            'id': self.id,
            'login': self.login,
            'mail': self.email,
            'name': self.name,
            'groups': [grp.name for grp in self.groups]
        }


class Group(db.Model):
    '''
    Représente un groupe de sécurité
    '''
    __tablename__ = 'auth_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(length=100))
    users = db.relationship('User', secondary='auth_rel_user_group')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'users': [user.id for user in self.users]
        }


class UserGroups(db.Model):
    '''
    Relations entre groupes et utilisateurs
    '''
    __tablename__ = 'auth_rel_user_group'
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('auth_utilisateur.id'),
        primary_key=True)
    group_id = db.Column(
        db.Integer,
        db.ForeignKey('auth_group.id'),
        primary_key=True)


class AuthUser:
    '''
    Classe représentant un utilisateur avec son nom et les groupes
    auxquels il appartient
    '''
    def __init__(self, data=None):
        try:
            self.id = data['id']
            self.name = data['name']
            self.groups = data['groups']
            self.mail = data['mail']
            self.is_valid = True
        except TypeError:
            self.id = None
            self.name = None
            self.mail = None
            self.groups = []
            self.is_valid = False

    def has_group(self, group):
        return group in self.groups

    @property
    def is_admin(self):
        return any([x in self.groups for x in [
            'admin-tizoutis',
            'Administrateurs']])

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'groups': self.groups,
            'mail': self.mail,
            'is_valid': self.is_valid
        }

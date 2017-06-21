#coding: utf8

'''
mapping machines
'''
from server import db


class Machine(db.Model):
    __tablename__ = 'sup_machine'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode(100))
    ip_addr = db.Column(db.Unicode(15))
    options = db.Column(db.Unicode(100))
    id_parent = db.Column(db.Integer)
    commentaire = db.Column(db.UnicodeText)

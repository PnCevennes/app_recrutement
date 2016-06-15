#coding: utf8

'''
mapping thésaurus
'''

from server import db


class Thesaurus(db.Model):
    __tablename__ = 'thesaurus'
    id = db.Column(db.Integer, primary_key=True)
    id_ref = db.Column(db.Integer)
    label = db.Column(db.Unicode(length=50))


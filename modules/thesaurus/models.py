#coding: utf8

'''
mapping thésaurus
'''

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Thesaurus(db.Model):
    __tablename__ = 'th_thesaurus'
    id = db.Column(db.Integer, primary_key=True)
    id_ref = db.Column(db.Integer)
    label = db.Column(db.Unicode(length=50))


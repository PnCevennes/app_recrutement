#coding: utf8

'''
mapping agent
'''

from server import db


class Agent(db.Model):
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode)
    prenom = db.Column(db.Unicode)
    service_id = db.Column(db.Integer) #TH ref 4
    desc_mission = db.Column(db.UnicodeText)
    type_contrat = db.Column(db.Integer) #TH ref 14
    lieu = db.Column(db.Integer) #TH ref 1
    arrivee = db.Column(db.Date)
    depart = db.Column(db.Date)
    logement = db.Column(db.Integer) #TH ref 10


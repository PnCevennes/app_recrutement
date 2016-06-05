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
    arrivee = db.Column(db.Date)
    depart = db.Column(db.Date)



class AgentDetail(Agent):
    __tablename__ = 'agent_detail'
    id_agent = db.Column(db.Integer, db.ForeignKey('agent.id'), primary_key=True)
    desc_mission = db.Column(db.UnicodeText)
    type_contrat = db.Column(db.Integer) #TH ref 14
    lieu = db.Column(db.Integer) #TH ref 1
    logement = db.Column(db.Integer) #TH ref 10


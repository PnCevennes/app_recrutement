#coding: utf8

'''
mapping agent
'''

from server import db


class Agent(db.Model):
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode(length=100))
    prenom = db.Column(db.Unicode(length=100))
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
    referent = db.Column(db.UnicodeText)
    materiel = db.relationship(
            'Thesaurus',
            secondary='rel_agent_thesaurus_materiel',
            lazy='joined')

    def to_json(self):
        out = {cn.name: getattr(self, cn.name)
                    for cn in super(AgentDetail, self).__table__.columns
                    if getattr(self, cn.name) is not None
                }
        out.update({cn.name: getattr(self, cn.name)
                    for cn in self.__table__.columns
                    if getattr(self, cn.name) is not None
                })
        out['arrivee'] = out['arrivee'].strftime('%Y-%m-%d')
        if 'depart' in out:
            out['depart'] = out['depart'].strftime('%Y-%m-%d')
        out['materiel'] = [item.id for item in self.materiel]
        return out



class RelAgentMateriel(db.Model):
    __tablename__ = 'rel_agent_thesaurus_materiel'
    id_agent = db.Column(
            db.Integer,
            db.ForeignKey('agent.id'),
            primary_key=True)
    id_thesaurus = db.Column(
            db.Integer,
            db.ForeignKey('thesaurus.id'),
            primary_key=True)


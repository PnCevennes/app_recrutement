#coding: utf8

'''
mapping agent
'''

from server import db


class Agent(db.Model):
    __tablename__ = 'recr_agent'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode(length=100))
    prenom = db.Column(db.Unicode(length=100))
    service_id = db.Column(db.Integer) #TH ref 4
    arrivee = db.Column(db.Date)
    depart = db.Column(db.Date)



class AgentDetail(Agent):
    __tablename__ = 'recr_agent_detail'
    id_agent = db.Column(db.Integer, db.ForeignKey('recr_agent.id'), primary_key=True)
    desc_mission = db.Column(db.UnicodeText)
    type_contrat = db.Column(db.Integer) #TH ref 14
    lieu = db.Column(db.Integer) #TH ref 1
    logement = db.Column(db.Integer) #TH ref 10
    categorie = db.Column(db.Integer) #TH ref 38
    referent = db.Column(db.UnicodeText)
    gratification = db.Column(db.Integer)
    temps_travail = db.Column(db.Integer) #TH ref 33
    temps_travail_autre = db.Column(db.Unicode(length=100))
    residence_administrative = db.Column(db.Unicode(length=100))
    observations = db.Column(db.UnicodeText)
    meta_create = db.Column(db.Date)
    meta_update = db.Column(db.Date)
    meta_createur_fiche = db.Column(db.Unicode(length=100))
    materiel = db.relationship(
            'Thesaurus',
            secondary='recr_rel_agent_thesaurus_materiel',
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
        out['meta_create'] = out['meta_create'].strftime('%Y-%m-%d')
        if 'meta_update' in out:
            out['meta_update'] = out['meta_update'].strftime('%Y-%m-%d')
        if 'depart' in out:
            out['depart'] = out['depart'].strftime('%Y-%m-%d')
        out['materiel'] = [item.id for item in self.materiel]
        return out



class RelAgentMateriel(db.Model):
    __tablename__ = 'recr_rel_agent_thesaurus_materiel'
    id_agent = db.Column(
            db.Integer,
            db.ForeignKey('recr_agent.id'),
            primary_key=True)
    id_thesaurus = db.Column(
            db.Integer,
            db.ForeignKey('th_thesaurus.id'),
            primary_key=True)


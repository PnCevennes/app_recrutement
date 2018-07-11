'''
mapping agent
'''

from server import db
from models import Fichier
from modules.thesaurus.models import Thesaurus


class Agent(db.Model):
    __tablename__ = 'recr_agent'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode(length=100))
    prenom = db.Column(db.Unicode(length=100))
    intitule_poste = db.Column(db.Unicode(length=255))
    service_id = db.Column(db.Integer)  # TH ref 4
    arrivee = db.Column(db.Date)
    depart = db.Column(db.Date)


class AgentDetail(Agent):
    __tablename__ = 'recr_agent_detail'
    id_agent = db.Column(
            db.Integer,
            db.ForeignKey('recr_agent.id'),
            primary_key=True)
    desc_mission = db.Column(db.UnicodeText)
    notif_list = db.Column(db.UnicodeText)
    type_contrat = db.Column(db.Integer)  # TH ref 14
    lieu = db.Column(db.Integer)  # TH ref 1
    logement = db.Column(db.Integer)  # TH ref 10
    categorie = db.Column(db.Integer)  # TH ref 38
    referent = db.Column(db.UnicodeText)
    gratification = db.Column(db.Integer)
    temps_travail = db.Column(db.Integer)  # TH ref 33
    temps_travail_autre = db.Column(db.Unicode(length=100))
    residence_administrative = db.Column(db.Unicode(length=100))
    convention_signee = db.Column(db.Boolean)
    bureau = db.Column(db.Unicode(length=50))
    observations = db.Column(db.UnicodeText)
    meta_create = db.Column(db.Date)
    meta_update = db.Column(db.Date)
    meta_createur_fiche = db.Column(db.Unicode(length=100))
    materiel = db.relationship(
            Thesaurus,
            secondary='recr_rel_agent_thesaurus_materiel',
            lazy='joined'
            )
    fichiers = db.relationship(
            Fichier,
            secondary='recr_rel_agent_fichier',
            lazy='joined'
            )

    def to_json(self):
        out = {
                cn.name: getattr(self, cn.name)
                for cn in super(AgentDetail, self).__table__.columns
                if getattr(self, cn.name) is not None}
        out.update({
                cn.name: getattr(self, cn.name)
                for cn in self.__table__.columns
                if getattr(self, cn.name) is not None})
        out['arrivee'] = str(out['arrivee'])
        if out.get('depart', None) is not None:
            out['depart'] = str(out['depart'])

        out['meta_create'] = str(out['meta_create'])
        if out.get('meta_update', None) is not None:
            out['meta_update'] = str(out['meta_update'])
        out['notif_list'] = [
                item for item in self.notif_list.split(',') if item]

        out['materiel'] = [item.id for item in self.materiel]
        out['fichiers'] = [item.to_json() for item in self.fichiers]
        return out


class RelAgentMateriel(db.Model):
    __tablename__ = 'recr_rel_agent_thesaurus_materiel'
    id_agent = db.Column(
            db.Integer,
            db.ForeignKey('recr_agent.id'),
            primary_key=True)
    id_thesaurus = db.Column(
            db.Integer,
            db.ForeignKey(Thesaurus.id),
            primary_key=True)


class RelAgentFichier(db.Model):
    __tablename__ = 'recr_rel_agent_fichier'
    id_agent = db.Column(
            db.Integer,
            db.ForeignKey('recr_agent.id'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id),
            primary_key=True)

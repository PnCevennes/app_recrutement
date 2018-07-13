'''
mapping agent
'''

from server import db
from models import Fichier, serialize_files
from modules.thesaurus.models import Thesaurus
from serialize_utils import (
    serializer,
    Serializer,
    Field,
    prepare_date,
    serialize_date)


@serializer
class AgentSerializer(Serializer):
    '''
    serialise une partie des données de la fiche pour
    un affichage en liste
    '''
    id = Field()
    nom = Field()
    prenom = Field()
    intitule_poste = Field()
    service_id = Field()
    arrivee = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )
    depart = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )


class Agent(db.Model):
    __tablename__ = 'recr_agent'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode(length=100))
    prenom = db.Column(db.Unicode(length=100))
    intitule_poste = db.Column(db.Unicode(length=255))
    service_id = db.Column(db.Integer)  # TH ref 4
    arrivee = db.Column(db.Date)
    depart = db.Column(db.Date)


@serializer
class AgentDetailSerializer(AgentSerializer):
    '''
    serialise la totalité de la fiche pour un affichage détaillé
    '''
    id_agent = Field()
    desc_mission = Field()
    notif_list = Field(
            serializefn=(
                lambda val: [item for item in val.split(',') if item]),
            preparefn=lambda val: ','.join(val)
            )
    type_contrat = Field()
    lieu = Field()
    logement = Field()  # TH ref 10
    categorie = Field()  # TH ref 38
    referent = Field()
    gratification = Field()
    temps_travail = Field()  # TH ref 33
    temps_travail_autre = Field()
    residence_administrative = Field()
    convention_signee = Field()
    bureau = Field()
    observations = Field()
    meta_create = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )
    meta_update = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )
    meta_createur_fiche = Field()
    materiel = Field(
            serializefn=lambda val: [item.id for item in val]
            )
    fichiers = Field(serializefn=serialize_files)


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

'''
mapping intervention
'''

from server import db
from models import Fichier, serialize_files
from serialize_utils import (
    serializer,
    Serializer,
    Field,
    prepare_date,
    serialize_date)


@serializer
class TravauxBatimentSerializer(Serializer):
    '''
    serialise une partie des données de la fiche pour
    un affichage en liste
    '''
    id = Field()
    dem_date = Field(
            serializefn=serialize_date,
            preparefn=prepare_date)
    dem_commune = Field()
    dem_designation = Field()
    rea_date = Field(
            serializefn=serialize_date,
            preparefn=prepare_date)


@serializer
class TravauxBatimentFullSerializer(TravauxBatimentSerializer):
    '''
    serialise la totalité de la fiche pour un affichage détaillé
    '''
    dmdr_service = Field()
    dmdr_contact_nom = Field()
    dmdr_contact_email = Field(
            serializefn=(
                lambda val: [item for item in val.split(',') if item]),
            preparefn=lambda val: ','.join(val)
            )
    dem_importance_travaux = Field()
    dem_type_travaux = Field()
    dem_description_travaux = Field()
    plan_service = Field()
    plan_entreprise = Field()
    plan_date = Field(
            serializefn=serialize_date,
            preparefn=prepare_date)
    plan_commentaire = Field()
    rea_duree = Field()
    rea_commentaire = Field()
    dem_fichiers = Field(serializefn=serialize_files)
    plan_fichiers = Field(serializefn=serialize_files)
    rea_fichiers = Field(serializefn=serialize_files)


class TravauxBatiment(db.Model):
    """
    Modele de fiche de travaux
    """
    __tablename__ = 'bati_travaux'
    id = db.Column(db.Integer, primary_key=True)
    dmdr_service = db.Column(db.Integer)
    dmdr_contact_nom = db.Column(db.Unicode(length=100))
    dmdr_contact_email = db.Column(db.Unicode(length=255))

    dem_date = db.Column(db.Date)
    dem_importance_travaux = db.Column(db.Integer)
    dem_type_travaux = db.Column(db.Integer)
    dem_description_travaux = db.Column(db.UnicodeText)
    dem_commune = db.Column(db.Integer)
    dem_designation = db.Column(db.Integer)

    plan_service = db.Column(db.Integer)
    plan_entreprise = db.Column(db.Unicode(255))
    plan_date = db.Column(db.Date)
    plan_commentaire = db.Column(db.UnicodeText)

    rea_date = db.Column(db.Date)
    rea_duree = db.Column(db.Integer)
    rea_commentaire = db.Column(db.UnicodeText)

    dem_fichiers = db.relationship(
            Fichier,
            secondary='bati_rel_travaux_fichier',
            lazy='joined'
            )

    plan_fichiers = db.relationship(
            Fichier,
            secondary='bati_rel_plan_fichier',
            lazy='joined'
            )

    rea_fichiers = db.relationship(
            Fichier,
            secondary='bati_rel_rea_fichier',
            lazy='joined'
            )


class TravauxFichier(db.Model):
    """
    relation entre la demande de travaux et les fichiers préparatoires
    """
    __tablename__ = 'bati_rel_travaux_fichier'
    id_demande = db.Column(
            db.Integer,
            db.ForeignKey('bati_travaux.id', ondelete='cascade'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id, ondelete='cascade'),
            primary_key=True)


class PlanFichier(db.Model):
    """
    relation entre la demande de travaux et les fichiers de planification
    """
    __tablename__ = 'bati_rel_plan_fichier'
    id_demande = db.Column(
            db.Integer,
            db.ForeignKey('bati_travaux.id', ondelete='cascade'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id, ondelete='cascade'),
            primary_key=True)


class ReaFichier(db.Model):
    """
    relation entre la demande de travaux et les fichiers justificatifs
    """
    __tablename__ = 'bati_rel_rea_fichier'
    id_demande = db.Column(
            db.Integer,
            db.ForeignKey('bati_travaux.id', ondelete='cascade'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id, ondelete='cascade'),
            primary_key=True)

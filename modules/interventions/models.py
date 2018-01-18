'''
mapping agent
'''

from server import db
from models import Fichier, serialize_files
from serialize_utils import serializer, Serializer, Field, prepare_date


@serializer
class DemandeSerializer(Serializer):
    id = Field()
    dem_date = Field(serializefn=str, preparefn=prepare_date)
    dem_objet = Field()
    dem_localisation = Field()
    dmdr_service = Field()
    rea_date = Field(
            serializefn=(lambda val: str(val) if val is not None else val),
            preparefn=prepare_date)


@serializer
class DemandeFullSerializer(DemandeSerializer):
    dem_loc_commune = Field()
    dem_loc_libelle = Field()
    dem_details = Field()
    dem_delai = Field()
    dem_fichiers = Field(serializefn=serialize_files)

    dmdr_contact_nom = Field()
    dmdr_contact_email = Field(
            serializefn=(
                lambda val: [item for item in val.split(',') if item]),
            preparefn=lambda val: ','.join(val)
            )

    plan_date = Field()
    plan_commentaire = Field()

    rea_duree = Field()
    rea_nb_agents = Field()
    rea_commentaire = Field()
    rea_fichiers = Field(serializefn=serialize_files)


class Demande(db.Model):
    """
    Modele de fiche d'intervention
    """
    __tablename__ = 'intv_demande'
    id = db.Column(db.Integer, primary_key=True)
    dem_date = db.Column(db.Date)
    dem_objet = db.Column(db.Integer)
    dem_localisation = db.Column(db.Integer)
    dem_loc_commune = db.Column(db.Unicode(length=100))
    dem_loc_libelle = db.Column(db.Unicode(length=100))
    dem_details = db.Column(db.UnicodeText)
    dem_delai = db.Column(db.Unicode(length=100))

    dmdr_service = db.Column(db.Integer)
    dmdr_contact_nom = db.Column(db.Unicode(length=100))
    dmdr_contact_email = db.Column(db.Unicode(length=255))

    plan_date = db.Column(db.Unicode(length=100))
    plan_commentaire = db.Column(db.UnicodeText)

    rea_date = db.Column(db.Date)
    rea_duree = db.Column(db.Integer)
    rea_nb_agents = db.Column(db.Integer)
    rea_commentaire = db.Column(db.UnicodeText)

    dem_fichiers = db.relationship(
            Fichier,
            secondary='intv_rel_demande_fichier',
            lazy='joined'
            )

    rea_fichiers = db.relationship(
            Fichier,
            secondary='intv_rel_rea_fichier',
            lazy='joined'
            )


class DemandeFichier(db.Model):
    """
    relation entre la demande et les fichiers préparatoires
    """
    __tablename__ = 'intv_rel_demande_fichier'
    id_demande = db.Column(
            db.Integer,
            db.ForeignKey('intv_demande.id'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id),
            primary_key=True)


class ReaFichier(db.Model):
    """
    relation entre la demande et les fichiers justificatifs
    de réalisation
    """
    __tablename__ = 'intv_rel_rea_fichier'
    id_demande = db.Column(
            db.Integer,
            db.ForeignKey('intv_demande.id'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id),
            primary_key=True)

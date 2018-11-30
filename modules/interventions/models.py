'''
mapping intervention
'''

from server import db
from core.models import Fichier, serialize_files


class Demande(db.Model):
    """
    Modele de fiche d'intervention
    """
    __tablename__ = 'intv_demande'
    id = db.Column(db.Integer, primary_key=True)
    num_intv = db.Column(db.Unicode(length=50))
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
            db.ForeignKey(Fichier.id, ondelete='cascade'),
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
            db.ForeignKey(Fichier.id, ondelete='cascade'),
            primary_key=True)

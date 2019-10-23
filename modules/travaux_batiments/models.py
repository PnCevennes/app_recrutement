'''
mapping intervention
'''

from server import db
from core.models import Fichier, file_relation


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
    rea_annulation = db.Column(db.Integer)

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


@file_relation('bati_trav')
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


@file_relation('bati_plan')
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


@file_relation('bati_rea')
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

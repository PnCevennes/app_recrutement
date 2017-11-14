#coding: utf8

'''
mapping agent
'''

from server import db
from models import Fichier
from modules.thesaurus.models import Thesaurus


class Demande(db.Model):
    """
    Modele de fiche d'intervention
    """
    __tablename__ = 'intv_demande'
    id = db.Column(db.Integer, primary_key=True)
    dem_date = db.Column(db.Date)
    dem_objet = db.Column(db.Integer)
    dem_localisation = db.Column(db.Integer)
    dem_details = db.Column(db.UnicodeText)
    dem_delai = db.Column(db.Unicode(length=100))

    dmdr_service = db.Column(db.Integer)
    dmdr_contact_nom = db.Column(db.Unicode(length=100))
    dmdr_contact_email = db.Column(db.Unicode(length=255))

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


    def to_json(self, full=False):
        fields = ['id', 'dem_date', 'dem_objet', 'dem_localisation',
                'dmdr_service', 'rea_date']
        if full:
            fields += ['dem_details', 'dem_delai', 'dmdr_contact_nom',
                    'dmdr_contact_email', 'rea_duree',
                    'rea_nb_agents', 'rea_commentaire', 'dem_fichiers',
                    'rea_fichiers']
        
        out = {k: getattr(self, k, '') for k in fields}
        out['dem_date'] = str(out['dem_date'])
        if out['rea_date'] is not None:
            out['rea_date'] = str(out['rea_date'])
        if 'dmdr_contact_email' in out and out['dmdr_contact_email'] is not None:
            out['dmdr_contact_email'] = [x for x in out['dmdr_contact_email'].split(',') if len(x.strip()) > 0]
            out['dem_fichiers'] = [item.to_json() for item in out['dem_fichiers']]
            out['rea_fichiers'] = [item.to_json() for item in out['rea_fichiers']]

        return out




class DemandeFichier(db.Model):
    """
    relation entre la demande et les fichiers préparatoires
    """
    __tablename__ = 'intv_rel_demande_fichier'
    id_demande= db.Column(
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
    id_demande= db.Column(
            db.Integer,
            db.ForeignKey('intv_demande.id'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id),
            primary_key=True)

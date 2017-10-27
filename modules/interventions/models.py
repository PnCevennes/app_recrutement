#coding: utf8

'''
mapping agent
'''

from server import db
from models import Fichier
from modules.thesaurus.models import Thesaurus


class Demande(db.Model):
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

    fichiers = db.relationship(
            Fichier,
            secondary='intv_rel_demande_fichier',
            lazy='joined'
            )

    def to_json(self, full=False):
        fields = ['id', 'dem_date', 'dem_objet', 'dem_localisation',
                'dmdr_service']
        if full:
            fields += ['dem_details', 'dem_delai', 'dmdr_contact_nom',
                    'dmdr_contact_email', 'rea_date', 'rea_duree',
                    'rea_nb_agents', 'fichiers']
        
        out = {k: getattr(self, k, '') for k in fields}
        out['dem_date'] = str(out['dem_date'])
        if 'dmdr_contact_email' in out:
            out['dmdr_contact_email'] = out['dmdr_contact_email'].split(',')
            out['fichiers'] = [item.to_json() for item in out['fichiers']]

        return out





class DemandeFichier(db.Model):
    __tablename__ = 'intv_rel_demande_fichier'
    id_demande= db.Column(
            db.Integer,
            db.ForeignKey('intv_demande.id'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id),
            primary_key=True)

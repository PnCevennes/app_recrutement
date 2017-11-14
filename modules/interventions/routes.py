#coding: utf8

'''
Routes relatives aux demandes d'intervention
'''
import datetime
from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound
from server import db as _db
from models import Fichier
from routes import upload_file, get_uploaded_file, delete_uploaded_file
from modules.thesaurus.models import Thesaurus
from modules.utils import normalize, json_resp, send_mail, register_module, registered_funcs
from .models import Demande, DemandeFichier


routes = Blueprint('interventions', __name__)

register_module('/interventions', routes)

check_auth = registered_funcs['check_auth']


@routes.route('/', methods=['GET'])
@json_resp
def get_interventions():
    """
    retourne la liste des demandes d'intervention
    """
    results = _db.session.query(Demande).all()
    return [res.to_json() for res in results]


@routes.route('/<id_intervention>', methods=['GET'])
@json_resp
def get_one_intervention(id_intervention):
    """
    retourne une demande d'intervention identifiée par id_intervention
    """
    result = _db.session.query(Demande).get(id_intervention)
    return result.to_json(full=True)


@routes.route('/', methods=['POST','PUT'])
@json_resp
def create_intervention():
    """
    crée une nouvelle demande d'intervention
    """
    dem = request.json
    dem['dem_fichiers'] = [_db.session.query(Fichier).get(item['id'])
            for item in dem.get('dem_fichiers', [])]
    dem['rea_fichiers'] = [_db.session.query(Fichier).get(item['id'])
            for item in dem.get('rea_fichiers', [])]
    dem['dem_date'] = datetime.datetime.now()
    dem['dmdr_contact_email'] = ','.join(dem.get('dmdr_contact_email',[]))

    demande = Demande(**dem)
    _db.session.add(demande)
    _db.session.commit()

    """
    send_mail(4, 6, "Création de la demande d'intervention n°%s" % demande.id,
            '''
            Une nouvelle demande d'intervention a été créée.
            Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions/%s pour voir les détails de cette demande.
            ''' % demande.id,
            add_dests = demande.dmdr_contact_email)
    """

    return {'id': demande.id}


@routes.route('/<id_intervention>', methods=['POST', 'PUT'])
@json_resp
def update_intervention(id_intervention):
    """
    met à jour une demande d'intervention identifée par id_intervention
    """
    dem = request.json
    dem['dem_fichiers'] = [_db.session.query(Fichier).get(item['id'])
            for item in dem.get('dem_fichiers', [])]
    dem['rea_fichiers'] = [_db.session.query(Fichier).get(item['id'])
            for item in dem.get('rea_fichiers', [])]
    dem['dem_date'] = datetime.datetime.strptime(dem['dem_date'], '%Y-%m-%d')
    if dem.get('rea_date') is not None and len(dem['rea_date']):
        try:
            dem['rea_date'] = datetime.datetime.strptime(dem['rea_date'], '%Y-%m-%d')
        except ValueError:
            dem['rea_date'] = datetime.datetime.strptime(dem['rea_date'], '%Y-%m-%dT%H:%M:%S.%fZ')

    dem['dmdr_contact_email'] = ','.join(dem.get('dmdr_contact_email',[]))

    demande = _db.session.query(Demande).get(id_intervention)
    for key, value in dem.items():
        setattr(demande, key, value)

    _db.session.commit()

    """
    send_mail(4, 6, "Mise à jour de la demande d'intervention n°%s" % demande.id,
            '''
            La demande d'intervention n°%s a été modifiée.
            Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions/%s pour voir les détails de cette demande.
            ''' % demande.id,
            add_dests = demande.dmdr_contact_email)
    """
    return {'id': demande.id}


@routes.route('/<id_intervention>', methods=['DELETE'])
@json_resp
def delete_intervention(id_intervention):
    """
    supprime une demande d'intervention identifiée par id_intervention
    """
    demande = _db.session.query(Demande).get(id_intervention)
    _db.session.delete(demande)
    _db.session.commit()
    """
    send_mail(4, 6, "Annulation de la demande d'intervention n°%s" % demande.id,
            '''
            La demande d'intervention n°%s a été annulée.
            Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions/ pour voir la liste des demandes en cours.
            ''',
            add_dests = demande.dmdr_contact_email)
    """
    return {'id': demande.id}

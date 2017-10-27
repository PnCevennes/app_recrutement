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
    print('create intervention')
    print(request.json)

    dem = request.json
    dem['fichiers'] = [_db.session.query(Fichier).get(item['id'])
            for item in dem.get('fichiers', [])]
    dem['dem_date'] = datetime.datetime.now()
    dem['dmdr_contact_email'] = ','.join(dem.get('dmdr_contact_email',[]))

    demande = Demande(**dem)
    _db.session.add(demande)
    _db.session.commit()

    """
    send_mail(4, 6, "Nouvelle demande d'intervention",
            '''
            Une nouvelle demande d'intervention a été créée.
            Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions/%s pour voir les détails de cette demande.
            ''' % dem.id,
            add_dests = dem.dmdr_contact_email)
    """

    return ['create intv']


@routes.route('/<id_intervention>', methods=['POST', 'PUT'])
@json_resp
def update_intervention(id_intervention):
    """
    met à jour une demande d'intervention identifée par id_intervention
    """
    print('update intervention')
    print(request.json)
    return ['update_intv']


@routes.route('/<id_intervention>', methods=['DELETE'])
@json_resp
def delete_intervention(id_intervention):
    """
    supprime une demande d'intervention identifiée par id_intervention
    """
    print('delete intervention')
    print(request.json)
    return ['delete_intv']

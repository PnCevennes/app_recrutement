'''
Routes relatives au thésurus
'''

from flask import Blueprint, request
from server import db as _db
from sqlalchemy.exc import StatementError

from core.thesaurus import models
from core.utils import (
        json_resp,
        register_module,
        registered_funcs
        )

routes = Blueprint('th_routes', __name__)

register_module('/thesaurus', routes)

check_auth = registered_funcs['check_auth']


@routes.route('/')
@json_resp
@check_auth(groups=['tizoutis-admin'])
def th_index():
    th_list = _db.session.query(models.Thesaurus).all()
    return [models.ThesaurusSerializer(item).serialize()
            for item in th_list]

@routes.route('/ref/<int:id_ref>')
@json_resp
def get_thesaurus(id_ref):
    '''
    effectue la requête sur la base de données en filtrant selon le
    parametre fourni.
    '''
    try:
        th_list = _db.session.query(models.Thesaurus).filter(
                models.Thesaurus.id_ref == id_ref).all()
        return [models.ThesaurusSerializer(item).serialize()
                for item in th_list]
    except StatementError:
        _db.session.rollback()
        return [], 400


@routes.route('/ref/<label>')
@json_resp
def get_th_mnemo(label):
    try:
        id_ref = _db.session.query(models.Thesaurus).filter(
            models.Thesaurus.label == label
            ).one()
        th_list = _db.session.query(models.Thesaurus).filter(
                models.Thesaurus.id_ref == id_ref.id).all()
        return [models.ThesaurusSerializer(item).serialize()
                for item in th_list]
    except StatementError:
        _db.session.rollback()
        return [], 400


@routes.route('/id/<id_thes>')
@json_resp
@check_auth(groups=['tizoutis-admin'])
def get_by_id(id_thes):
    result = _db.session.query(models.Thesaurus).get(int(id_thes))
    if not result:
        return [], 404
    return {'id': result.id, 'label': result.label}


@routes.route('/', methods=['PUT', 'POST'])
@json_resp
@check_auth(groups=['tizoutis-admin'])
def create_thesaurus():
    thes = models.Thesaurus()
    thes.id_ref = request.json['id_ref']
    thes.label = request.json['label']
    _db.session.add(thes)
    _db.session.commit()
    return {'value': 'ok'}


@routes.route('/<int:id_ref>', methods=['PUT', 'POST'])
@json_resp
@check_auth(groups=['tizoutis-admin'])
def update_thesaurus(id_ref):
    result = _db.session.query(models.Thesaurus).get(id_ref)
    result.label = request.json.get('label', '')
    _db.session.commit()
    return {'value': 'ok'}


@routes.route('/<int:id_ref>', methods=['DELETE'])
@json_resp
@check_auth(groups=['tizoutis-admin'])
def delete_thesaurus(id_ref):
    result = _db.session.query(models.Thesaurus).get(id_ref)
    _db.session.delete(result)
    _db.session.commit()
    return {'value': 'ok'}

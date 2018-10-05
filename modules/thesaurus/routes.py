'''
Routes relatives au thésurus
'''

from flask import Blueprint
from server import db as _db
from sqlalchemy.exc import StatementError

from modules.thesaurus import models
from modules.utils import normalize, json_resp, register_module

routes = Blueprint('th_routes', __name__)

register_module('/thesaurus', routes)


@routes.route('/')
@json_resp
def th_index():
    th_list = _db.session.query(models.Thesaurus).all()
    return [normalize(item) for item in th_list]

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
        return [normalize(item) for item in th_list]
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
        return [normalize(item) for item in th_list]
    except StatementError:
        _db.session.rollback()
        return [], 400


@routes.route('/id/<id_thes>')
@json_resp
def get_by_id(id_thes):
    result = _db.session.query(models.Thesaurus).get(int(id_thes))
    if not result:
        return [], 404
    return {'id': result.id, 'label': result.label}

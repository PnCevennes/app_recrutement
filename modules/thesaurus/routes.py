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


@routes.route('/ref/<id_ref>')
@json_resp
def get_thesaurus(id_ref):
    '''
    effectue la requête sur la base de données en filtrant selon le
    parametre fourni.
    '''
    try:
        th_list = _db.session.query(models.Thesaurus).filter(
                models.Thesaurus.id_ref == id_ref).all()
        out = []
        for item in th_list:
            out.append(normalize(item))
        return out
    except StatementError:
        _db.session.rollback()
        return [], 400


@routes.route('/id/<id_thes>')
@json_resp
def get_by_id(id_thes):
    result = models.Thesaurus.query.get(id_thes)
    if not result:
        return [], 404
    return {'id': result.id, 'label': result.label}

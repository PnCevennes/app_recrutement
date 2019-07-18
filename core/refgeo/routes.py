from flask import Blueprint
from server import db
from sqlalchemy.exc import StatementError

from core.refgeo import models
from core.utils import json_resp, register_module

routes = Blueprint('rg_routes', __name__)

register_module('/refgeo', routes)


@routes.route('/commune')
@json_resp
def get_communes():
    try:
        com_list = db.session.query(models.RefGeoCommunes).all()
        out = []
        for item in com_list:
            out.append({'id': item.id, 'label': item.nom_commune})
        return out
    except StatementError:
        db.session.rollback()
        return [], 400


@routes.route('/commune/id/<id_com>')
@json_resp
def get_one_commune(id_com):
    result = db.session.query(models.RefGeoCommunes).get(int(id_com))
    if not result:
        return [], 404
    return {'id': result.id, 'label': result.nom_commune}


@routes.route('/batiment')
@json_resp
def get_all_batiments():
    bat_list = db.session.query(models.RefGeoBatiment).all()
    out = []
    for result in bat_list:
        out.append({
            'id': result.id,
            'ref_commune': result.ref_commune,
            'label': '[%s] - %s - %s' % (
                result.reference,
                result.lieu_dit,
                result.designation
            )
        })
    return out


@routes.route('/batiment/<id_com>')
@json_resp
def get_batiments_by_commune(id_com):
    bat_list = db.session.query(models.RefGeoBatiment).filter(
        models.RefGeoBatiment.ref_commune == id_com
    ).all()
    out = []
    for result in bat_list:
        out.append({'id': result.id, 'label': '[%s] - %s - %s' % (
            result.reference,
            result.lieu_dit,
            result.designation
        )})
    return out


@routes.route('/batiment/id/<id_bat>')
@json_resp
def get_one_batiment(id_bat):
    result = db.session.query(models.RefGeoBatiment).get(int(id_bat))
    if not result:
        return [], 404
    return {
        'id': result.id,
        'label': '[%s] - %s - %s' % (
            result.reference,
            result.lieu_dit,
            result.designation
        )
    }

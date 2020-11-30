import json
import datetime

from flask import Blueprint, request
from server import db as _db, get_app
from core.utils import json_resp, register_module
from core.utils.serialize import ValidationError
from .models import Equipement, EquipementSerializer

routes = Blueprint('superv', __name__)

register_module('/supervision', routes)

app = get_app()

if app.config.get('ENABLE_SUPERVISION', False):
    from . import tools


@routes.route('/')
@json_resp
def sup_index():
    fields = ['id', 'ip_addr', 'label', 'equip_type', 'last_up', 'status']
    conn = _db.engine.connect()
    results = conn.execute('select %s from sup_equipement' % ', '.join(fields))
    out = []
    for item in results:
        item = map(lambda x: str(x) if x is not None else None, item)
        out.append({key: value for key, value in zip(fields, item)})

    return out


@routes.route('/<id_equip>', methods=['GET'])
@json_resp
def get_one_equip(id_equip):
    result = _db.session.query(Equipement).get(id_equip)
    if result:
        return EquipementSerializer(result).dump()
    else:
        return [], 404


@routes.route('/', methods=['POST', 'PUT'])
@json_resp
def create_equip():
    data = request.json
    equip = Equipement()
    try:
        EquipementSerializer(equip).load(data)
        _db.session.add(equip)
        _db.session.commit()
        return EquipementSerializer(equip).dump()
    except ValidationError as err:
        return err.errors, 400


@routes.route('/<id_equip>', methods=['POST', 'PUT'])
@json_resp
def update_equip(id_equip):
    data = request.json
    equip = _db.session.query(Equipement).get(id_equip)
    if not equip:
        return [], 404
    try:
        EquipementSerializer(equip).load(data)
        _db.session.commit()
        return EquipementSerializer(equip).dump()
    except ValidationError as err:
        return err.errors, 400


@routes.route('/<id_equip>', methods=['DELETE'])
@json_resp
def delete_equip(id_equip):
    equip = _db.session.query(Equipement).get(id_equip)
    if not equip:
        return [], 404
    _db.session.delete(equip)
    _db.session.commit()
    return {'id': equip.id}

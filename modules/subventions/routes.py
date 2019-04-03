import datetime

from flask import Blueprint, request, Response
from werkzeug.datastructures import Headers

from server import db as _db
from core.models import Fichier, prepare_fichiers, get_chrono, amend_chrono
from core.routes import upload_file, get_uploaded_file, delete_uploaded_file
from core.thesaurus.models import Thesaurus
from core.utils import (
        json_resp,
        send_mail,
        register_module,
        registered_funcs
        )
from core.utils.serialize import ValidationError
from .models import DemandeSubvention 
from .serializers import SubvSerializer, SubvFullSerializer


SubvFullSerializer.sub_fichiers.preparefn = prepare_fichiers(_db)
SubvFullSerializer.dec_fichiers.preparefn = prepare_fichiers(_db)
SubvFullSerializer.pai_fichiers.preparefn = prepare_fichiers(_db)


routes = Blueprint('subventions', __name__)

register_module('/subventions', routes)

check_auth = registered_funcs['check_auth']


@routes.route('/')
@json_resp
def get_subs():
    print('subs')
    subs = _db.session.query(DemandeSubvention).all()
    return [SubvSerializer(sub).serialize() for sub in subs]


@routes.route('/{id_sub:int}')
@json_resp
def get_detail_subv(id_sub):
    subv = _db.session.query(DemandeSubvention).get(id_sub)
    return SubvFullSerializer(subv).serialize()


@routes.route('/', methods=['POST', 'PUT'])
@json_resp
def create_subv():
    dem = request.json
    ref_chrono = '{}S'.format(dem['sub_date_rcpt'][2:4])
    demande = DemandeSubvention()
    try:
        dem['meta_id'] = get_chrono(ref_chrono)
        SubvFullSerializer(demande).populate(dem)
        _db.session.add(demande)
        _db.session.commit()
        return {'id': demande.id, 'meta_id': demande.meta_id}
    except ValidationError as e:
        amend_chrono(ref_chrono)
        return e.errors, 400


@routes.route('/{id_sub:int}', methods=['POST', 'PUT'])
@json_resp
def update_subv(id_sub):
    dem = request.json
    demande = _db.session.query(DemandeSubvention).get(id_sub)
    if not demande:
        return {}, 404
    try:
        SubvFullSerializer(demande).populate(dem)
        _db.session.commit()
        return SubvFullSerializer(demande).serialize()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/{id_sub:int}', methods=['DELETE'])
@json_resp
def delete_subv(id_sub):
    demande = _db.session.query(DemandeSubvention).get(id_sub)
    if not demande:
        return {}, 404
    _db.session.delete(demande)
    _db.session.commit()
    return {'id': demande.id}

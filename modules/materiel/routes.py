from flask import Blueprint, request, Response

from server import db

from core.utils import (
    json_resp,
    register_module,
    registered_funcs
)
from core.utils.serialize import ValidationError

from .models import (
    TypeMateriel,
    Materiel,
    Affectation
)
from .serializers import (
    TypeMaterielSerializer,
    MaterielSerializer,
    MaterielFullSerializer,
    AffectationSerializer
)


routes = Blueprint('materiel', __name__)
register_module('/materiel', routes)

check_auth = registered_funcs['check_auth']


@routes.route('/')
@json_resp
@check_auth(groups=['admin-tizoutis'])
def get_materiels():
    '''
    retourne la liste du matériel
    '''
    params = request.args.getlist('itemType')
    req = db.session.query(Materiel)
    if len(params):
        req = req.filter(Materiel.type_mat.in_(params))
        res = req.all()
        return [MaterielSerializer(mat).dump() for mat in res]
    return []


@routes.route('/<id_mat>', methods=['GET'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def get_detail_materiel(id_mat):
    '''
    retourne le détail d'un matériel
    '''
    mat = db.session.query(Materiel).get(id_mat)
    if not mat:
        return {}, 404
    return MaterielFullSerializer(mat).dump()


@routes.route('/', methods=['POST', 'PUT'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def create_materiel():
    '''
    cree un nouveau materiel
    '''
    mat = Materiel()
    data = request.json
    try:
        ser = MaterielFullSerializer(mat)
        ser.load(data)
        db.session.add(mat)
        db.session.commit()
        return ser.dump()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<id_mat>', methods=['POST'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def update_materiel(id_mat):
    mat = db.session.query(Materiel).get(id_mat)
    data = request.json
    if not mat:
        return {}, 404
    try:
        mat_serializer = MaterielFullSerializer(mat)
        mat_serializer.load(data)
        db.session.commit()
        return mat_serializer.dump()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<id_mat>', methods=['PUT'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def update_dsp_materiel(id_mat):
    mat = db.session.query(Materiel).get(id_mat)
    data = request.json
    if not mat:
        return {}, 404
    try:
        mat_serializer = MaterielFullSerializer(mat)
        mat_serializer.disponible = int(data['disponible'])
        mat_serializer.utilisateur_actuel = data['utilisateur_actuel']
        db.session.commit()
        return mat_serializer.dump()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<id_mat>', methods=['DELETE'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def delete_materiel(id_mat):
    mat = db.session.query(Materiel).get(id_mat)
    if not mat:
        return {}, 404
    db.session.delete(mat)
    return {'id': mat.id}


@routes.route('/types', methods=['GET'])
@json_resp
def get_types():
    '''
    retourne la liste des types de matériel
    '''
    types = db.session.query(TypeMateriel).all()
    return [TypeMaterielSerializer(tmat).dump() for tmat in types]


@routes.route('/types', methods=['POST', 'PUT'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def create_type():
    typ_mat = TypeMateriel()
    data = request.json
    typ_mat_ser = TypeMaterielSerializer(typ_mat)
    try:
        typ_mat_ser.load(data)
        db.session.add(typ_mat)
        db.session.commit()
        return typ_mat_ser.dump()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/types/search/<txt>', methods=['GET'])
@json_resp
def search_type(txt):
    types = db.session.query(TypeMateriel).filter(
            TypeMateriel.label.ilike(txt+'%')).all()
    return [TypeMaterielSerializer(typ).dump(('id', 'label')) for typ in types]


@routes.route('/types/<id_type>', methods=['POST', 'PUT'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def update_type(id_type):
    typ_mat = db.session.query(TypeMateriel).get(id_type)
    data = request.json
    typ_mat_ser = TypeMaterielSerializer(typ_mat)
    try:
        typ_mat_ser.load(data)
        db.session.commit()
        return typ_mat_ser.dump()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/affectations/<id_mat>', methods=['GET'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def get_affectations(id_mat):
    affs = db.session.query(Affectation).filter(
        Affectation.id_materiel == id_mat
    ).order_by(Affectation.date_affectation).all()
    return [AffectationSerializer(aff).dump() for aff in affs]


@routes.route('/affectation', methods=['POST', 'PUT'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def create_affectation():
    aff = Affectation()
    aff_ser = AffectationSerializer(aff)
    data = request.json
    try:
        aff_ser.load(data)
        db.session.add(aff)
        db.session.commit()
        return aff_ser.dump()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/affectation/<id_aff>', methods=['POST', 'PUT'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def update_affectation(id_aff):
    aff = db.session.query(Affectation).get(id_aff)
    data = request.json
    if not aff:
        return {}, 404
    aff_ser = AffectationSerializer(aff)
    try:
        aff_ser.load(data)
        db.session.commit()
        return aff_ser.dump()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/affectation/<id_aff>', methods=['DELETE'])
@json_resp
@check_auth(groups=['admin-tizoutis'])
def delete_affectation(id_aff):
    aff = db.session.query(Affectation).get(id_aff)
    if not aff:
        return {}, 404
    db.session.delete(aff)
    db.session.commit()
    return {'id': aff.id}

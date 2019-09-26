'''
routes relatives à l'annuaire
'''
import datetime

from flask import Blueprint, request, Response, g
from sqlalchemy.exc import InvalidRequestError

from server import db as _db
from core.utils import (
    json_resp,
    csv_response,
    vcard_response,
    register_module,
    registered_funcs)
from core.utils.serialize import ValidationError
# from core.models import record_changes, load_changes, ChangeType

from .models import (
    Entite,
    Commune,
    Correspondant,
    Entreprise,
    RelationEntite)
from .serializers import (
    EntiteSerializer,
    CommuneSerializer,
    CorrespondantSerializer,
    EntrepriseSerializer
)
from .utils import format_vcard


routes = Blueprint('annuaire', __name__)

register_module('/annuaire', routes)

check_auth = registered_funcs['check_auth']

TYPES_E = {
    'entite': (Entite, EntiteSerializer),
    'commune': (Commune, CommuneSerializer),
    'correspondant': (Correspondant, CorrespondantSerializer),
    'entreprise': (Entreprise, EntrepriseSerializer)
}

FIELDS_E = {
    'entite': [
        'id',
        'nom',
        'observations'],
    'commune': [
        'id',
        'nom',
        'adresse',
        'adresse2',
        'code_postal',
        'telephone',
        'email',
        'site_internet'],
    'correspondant': [
        'id',
        'civilite',
        'nom',
        'prenom',
        'adresse',
        'adresse2',
        'code_postal',
        'telephone',
        'mobile',
        'email'],
    'entreprise': [
        'id',
        'nom',
        'adresse',
        'adresse2',
        'code_postal',
        'nom_gerant',
        'prenom_gerant',
        'telephone',
        'telephone2',
        'email',
        'alt_email',
        'site_internet'],
}


@routes.route('/entites')
@json_resp
@check_auth()
def get_entites():
    '''
    retourne la liste des groupes
    '''
    entite_ids = request.args.getlist('params')
    _format = request.args.get('format', None)
    _etype = request.args.get('type', 'correspondant')
    if not len(entite_ids):
        if not request.args.get('all', False):
            return {}
        entites = Entite.query.all()
    else:
        parents = Entite.query.filter(Entite.id.in_(entite_ids)).all()
        filters = [Entite.parents.contains(z) for z in parents]
        entites = Entite.query.filter(_db.and_(*filters)).order_by(Entite.type_entite).order_by(Entite.nom).all()
    if _format in ('csv', 'tsv'):
        ent_type, serializer = TYPES_E[_etype]
        entites = filter(lambda x: isinstance(x, ent_type), entites)
        if _format == 'csv':
            csv = serializer.export_csv(entites, fields=FIELDS_E[_etype])
        else:
            csv = serializer.export_csv(
                entites,
                fields=FIELDS_E[_etype],
                sep='\t'
            )
        return csv_response(csv, 'annuaire.csv')
    if _format == 'vcard':
        vcards = '\r\n'.join([
            format_vcard(CorrespondantSerializer(e)) for e in entites
            if isinstance(e, Correspondant)
        ])
        return vcard_response(vcards, 'annuaire.vcf')

    return {
        'recherche': [TYPES_E[e.type_entite][1](e).dump() for e in parents],
        'liste': [TYPES_E[e.type_entite][1](e).dump() for e in entites]
    }


@routes.route('/entite/<id_entite>')
@json_resp
@check_auth()
def get_entite(id_entite):
    '''
    retourne une entite
    '''
    entite_type = request.args.get('type', 'entite')
    _format = request.args.get('format', None)
    entitecls, serializer = TYPES_E[entite_type]
    entite = entitecls.query.get(id_entite)
    if not entite:
        return {'errmsg': 'Donnée inexistante'}, 404
    if _format == 'vcard':
        filename = entite.label.encode('ascii', 'ignore') + b'.vcf'
        vcard = format_vcard(entite)
        return vcard_response(vcard, filename)
    out = serializer(entite).dump()
    # out['meta_changelog'] = load_changes(entite)
    return out


@routes.route('/entites/<nom>')
@json_resp
def get_entite_nom(nom):
    '''
    retourne les entites correspondant à nom
    '''
    # type d'entite à retourner (entite=tous les types)
    entite_type = request.args.get('type', 'entite')

    # type de résultat (obj=id, label)
    entite_result = request.args.get('result', 'obj')

    # colonne de retour ID
    entite_col = request.args.get('col', 'id')

    entite_filtre = request.args.get('filter', 'label')
    recherche = '%s%%' % '% '.join(nom.split())
    t_entite, _ = TYPES_E[entite_type]
    try:
        entites = (
            t_entite.query
            .filter(getattr(t_entite, entite_filtre).like(recherche))
            .order_by(getattr(t_entite, entite_filtre))
            .all()
        )
    except AttributeError:
        entite_filtre = 'label'
        entites = (
            t_entite.query
            .filter(getattr(t_entite, entite_filtre).like(recherche))
            .order_by(getattr(t_entite, entite_filtre))
            .all()
        )
    if entite_result == 'obj':
        return [
            {
                'id': getattr(e, entite_col, None),
                'label': e.label,
                'fonction': getattr(e, 'fonction', None)
            }
            for e in entites
        ]
    return [getattr(e, entite_col, None) for e in entites]


@routes.route('/lib_entites/')
@json_resp
def get_lib_entite():
    '''
    retourne un dictionnaire id/label
    '''
    entite_ids = request.args.getlist('params')
    if not len(entite_ids):
        entites = Entite.query.all()
    else:
        entites = Entite.query.filter(Entite.id.in_(entite_ids)).all()
    return [
        {
            'id': item.id,
            'label': item.label,
            'fonction': getattr(item, 'fonction', '')
        } for item in entites
    ]


@routes.route('/entite', methods=['POST', 'PUT'])
@json_resp
@check_auth(['tizoutis-annuaire'])
def create_entite():
    '''
    cree une nouvelle entite
    '''
    data = request.json
    entite_type = data.get('type_entite', 'entite')
    _entite, _serializer = TYPES_E[entite_type]
    entite = _entite()
    serializer = _serializer(entite)
    try:
        serializer.populate(data)
        # record_changes(entite, {}, ChangeType.CREATE)
    except ValidationError as e:
        return {'errors': e.errors}, 400
    _db.session.add(entite)
    '''
    serializer.parents = parents
    serializer.relations = relations
    '''
    _db.session.commit()
    return serializer.dump()


@routes.route('/entite/<id_entite>', methods=['POST', 'PUT'])
@json_resp
@check_auth(['tizoutis-annuaire'])
def update_entite(id_entite):
    '''
    met à jour une entite
    '''
    data = request.json
    entite = Entite.query.get(id_entite)
    _, _serializer = TYPES_E[entite.type_entite]
    serializer = _serializer(entite)
    try:
        serializer.load(data)
        # record_changes(entite, serializer.changelog, ChangeType.UPDATE)
    except ValidationError as e:
        return {'errors': e.errors}, 400
    _db.session.commit()
    return serializer.dump()


@routes.route('/entite/<id_entite>', methods=['DELETE'])
@json_resp
@check_auth(['tizoutis-annuaire'])
def delete_entite(id_entite):
    entite = _db.session.query(Entite).get(id_entite)
    if not entite:
        return {'errmsg': 'Donnée inexistante'}, 404
    _, _serializer = TYPES_E[entite.type_entite]
    serializer = _serializer(entite)
    try:
        _db.session.delete(entite)
        _db.session.commit()
        # record_changes(entite, serializer.dump(), ChangeType.DELETE)
    except InvalidRequestError as excpt:
        _db.session.rollback()
        return {
            'msg': 'Erreur à la suppression',
            'trace': str(excpt)
        }, 500
    return []

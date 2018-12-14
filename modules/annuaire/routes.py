'''
routes relatives à l'annuaire
'''
import datetime

from flask import Blueprint, request, Response

from server import db as _db
from core.utils import (
        json_resp,
        csv_response,
        vcard_response,
        register_module,
        registered_funcs)

from .models import (
        Entite, EntiteValidateur,
        Commune, CommuneValidateur,
        Correspondant, CorrespondantValidateur,
        Entreprise, EntrepriseValidateur,
        RelationEntite, ValidationError)
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
        'entite': Entite,
        'commune': Commune,
        'correspondant': Correspondant,
        'entreprise': Entreprise
        }

SERIALIZERS_E = {
        'entite': EntiteSerializer,
        'commune': CommuneSerializer,
        'correspondant': CorrespondantSerializer,
        'entreprise': EntrepriseSerializer
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



def get_entites_by_parent(entite_ids):
    '''
    retourne une liste d'entites "enfants" de la liste d'ID fournie
    '''
    rels = (RelationEntite.query
            .filter(RelationEntite.id_parent.in_(entite_ids))
            .all())
    all_ids = [item.id_enfant for item in rels]
    ids = set(filter(lambda x: all_ids.count(x) == len(entite_ids), all_ids))
    ids = ids | set(entite_ids)
    return (Entite.query
            .filter(Entite.id.in_(ids))
            .order_by(Entite.type_entite)
            .order_by(Entite.label)
            .all())



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
        entites = Entite.query.all()
    else:
        entites = get_entites_by_parent(entite_ids)
    if _format in ('csv', 'tsv'):
        serializer = SERIALIZERS_E[_etype]
        entites = filter(lambda x: isinstance(x, TYPES_E[_etype]) ,entites)
        if _format == 'csv':
            csv = serializer.export_csv(entites, fields=FIELDS_E[_etype])
        else:
            csv = serializer.export_csv(entites, fields=FIELDS_E[_etype], sep='\t')
        return csv_response(csv, 'annuaire.csv')
    if _format == 'vcard':
        vcards = '\r\n'.join([
                format_vcard(CorrespondantSerializer(e)) for e in entites
                if isinstance(e, Correspondant)
                ])
        return vcard_response(vcards, 'annuaire.vcf')

    return [SERIALIZERS_E[e.type_entite](e).serialize() for e in entites]


@routes.route('/entite/<id_entite>')
@json_resp
@check_auth()
def get_entite(id_entite):
    '''
    retourne une entite
    '''
    entite_type = request.args.get('type', 'entite')
    _format = request.args.get('format', None)
    entite = TYPES_E[entite_type].query.get(id_entite)
    if not entite:
        return {'errmsg': 'Donnée inexistante'}, 404
    if _format == 'vcard':
        headers = Headers()
        headers.add('Content-Type', 'text/plain')
        headers.add(
                'Content-Disposition',
                'attachment',
                filename=entite.label.encode('ascii', 'ignore')+b'.vcf')
        vcard = format_vcard(entite)
        return Response(vcard, headers=headers)
    return SERIALIZERS_E[entite.type_entite](entite).serialize()


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
    t_entite = TYPES_E[entite_type]
    entites = (
            t_entite.query
            .filter(getattr(t_entite, entite_filtre).like(recherche))
            .order_by(getattr(t_entite, entite_filtre))
            .all())
    if entite_result == 'obj':
        return [
                {
                    'id': getattr(e, entite_col, None),
                    'label': e.label,
                    'fonction': getattr(e, 'fonction', None)
                }
                for e in entites]
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
    return [{'id': item.id, 'label': item.label, 'fonction': getattr(item, 'fonction', '')} for item in entites]


@routes.route('/entite', methods=['POST', 'PUT'])
@json_resp
@check_auth(['tizoutis-annuaire'])
def create_entite():
    '''
    cree une nouvelle entite
    '''
    data = request.json
    entite_type = data.get('type_entite', 'entite')
    entite = TYPES_E[entite_type]()
    serializer = SERIALIZERS_E[entite_type](entite)
    parents = data.pop('parents', [])
    relations = data.pop('relations', [])
    try:
        serializer.populate(data)
    except ValidationError as e:
        return {'errors': e.errors}, 400
    _db.session.add(entite)
    serializer.parents = parents
    serializer.relations = relations
    _db.session.commit()
    return serializer.serialize()


@routes.route('/entite/<id_entite>', methods=['POST', 'PUT'])
@json_resp
@check_auth(['tizoutis-annuaire'])
def update_entite(id_entite):
    '''
    met à jour une entite
    '''
    data = request.json
    entite_type = data.get('type_entite', 'entite')
    entite = Entite.query.get(id_entite)
    serializer = SERIALIZERS_E[entite_type](entite)
    try:
        serializer.populate(data)
    except ValidationError as e:
        return {'errors': e.errors}, 400
    _db.session.commit()
    return serializer.serialize()


@routes.route('/entite/<id_entite>', methods=['DELETE'])
@json_resp
@check_auth(['tizoutis-annuaire'])
def delete_entite(id_entite):
    entite = Entite.query.get(id_entite)
    if not entite:
        return {'errmsg': 'Donnée inexistante'}, 404
    try:
        entite.delete_relations()
    except sqlalchemy.exc.InvalidRequestError:
        _db.session.rollback()
    _db.session.delete(entite)
    _db.session.commit()
    return []

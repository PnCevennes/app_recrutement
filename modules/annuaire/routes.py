#coding: utf8

'''
routes relatives à l'annuaire
'''
from flask import Blueprint, request, Response
from werkzeug.datastructures import Headers
from sqlalchemy.orm.exc import NoResultFound
from .models import (
        Entite, EntiteValidateur, 
        Commune, CommuneValidateur,
        Correspondant, CorrespondantValidateur,
        RelationEntite)
from ..utils import normalize, json_resp, register_module
from server import db
import datetime

routes = Blueprint('annuaire', __name__)

register_module('/annuaire', routes)


TYPES_E = {
        'entite': Entite,
        'commune': Commune,
        'correspondant': Correspondant,
        }


VALIDATEURS_E = {
        'entite': EntiteValidateur,
        'commune': CommuneValidateur,
        'correspondant': CorrespondantValidateur,
        }

vcard_tpl = '''BEGIN:VCARD
VERSION:2.1
N:%s;%s
FN:%s
TEL;WORK;VOICE:%s%s
EMAIL;PREF;INTERNET:%s
REV:%s
END:VCARD'''


def format_vcard(entite):
    '''
    retourne une vcard formatee selon les donnees de l'entite fournie
    '''
    dtime = datetime.datetime.now()
    return vcard_tpl % (
        entite.nom or '',
        entite.prenom or '',
        entite.label or '',
        format_phone(entite.telephone),
        "\nTEL;CELL;VOICE:%s" % format_phone(entite.mobile) if entite.mobile else '',
        entite.email or '',
        dtime.strftime('%Y%m%dT%H%m%SZ')
        )


def format_csv(corresps, sep=','):
    '''
    retourne une liste de correspondants sous format tabulaire CSV
    '''
    if not len(corresps):
        return ''

    correspondants = [normalize(corresp) for corresp in corresps]
    for corr in correspondants:
        del corr['parents']
        del corr['relations']
    fields = correspondants[0].keys()
    outdata = [sep.join(fields)]
    for item in correspondants:
        outdata.append(sep.join([str((e or '')) for e in item.values()]))
    return '\r\n'.join(outdata)
    '''
    return \r\n' + '\r\n'.join([','.join((
            corresp.civilite or '',
            corresp.nom or '',
            corresp.prenom or '',
            corresp.adresse or '',
            corresp.fonction or '')) for corresp in corresps])
    '''





def get_entites_by_parent(entite_ids):
    '''
    retourne une liste d'entites "enfants" de la liste d'ID fournie
    '''
    rels = RelationEntite.query.filter(RelationEntite.id_parent.in_(entite_ids)).all()
    all_ids = [item.id_enfant for item in rels]
    ids = set(filter(lambda x: all_ids.count(x)==len(entite_ids), all_ids))
    ids = ids | set(entite_ids)
    return Entite.query.filter(Entite.id.in_(ids)).order_by(Entite.type_entite).order_by(Entite.label).all()


def format_phone(tel):
    '''
    formate un noméro de téléphone
    '''
    try:
        return ' '.join(a+b for a,b in zip([x for x in tel[::2]], [y for y in tel[1::2]]))
    except:
        return tel




@routes.route('/entites')
@json_resp
def get_entites():
    '''
    retourne la liste des groupes
    '''
    entite_ids = request.args.getlist('params')
    _format = request.args.get('format', None)
    if not entite_ids:
        entites = Entite.query.all()
    else:
        entites = get_entites_by_parent(entite_ids)
    if _format in ('csv', 'tsv'):
        headers = Headers()
        headers.add('Content-Type', 'text/plain')
        headers.add('Content-Disposition', 'attachment', filename='export.csv')
        if _format == 'csv':
            csv = format_csv([e for e in entites if isinstance(e, Correspondant)], ',')
        else:
            csv = format_csv([e for e in entites if isinstance(e, Correspondant)], '\t')
        return Response(csv, headers=headers)
    if _format == 'vcard':
        headers = Headers()
        headers.add('Content-Type', 'text/plain')
        headers.add('Content-Disposition', 'attachment', filename='export.vcf')
        vcards = '\r\n'.join([format_vcard(e) for e in entites
            if isinstance(e, Correspondant)])
        return Response(vcards, headers=headers)

    return [normalize(e) for e in entites]# if isinstance(e, (Commune, Correspondant))]



@routes.route('/entite/<id_entite>')
@json_resp
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
        headers.add('Content-Disposition', 'attachment', filename=entite.label.encode('ascii', 'ignore')+b'.vcf')
        vcard = format_vcard(entite)
        return Response(vcard, headers=headers)
    return normalize(entite)



@routes.route('/entites/<nom>')
@json_resp
def get_entite_nom(nom):
    '''
    retourne les entites correspondant à nom
    '''
    entite_type = request.args.get('type', 'entite')
    recherche = '%s%%' % '% '.join(nom.split())
    t_entite = TYPES_E[entite_type]
    entites = t_entite.query.filter(t_entite.label.like(recherche)).all()
    return [{'id': e.id, 'label': e.label} for e in entites]



@routes.route('/lib_entites/')
@json_resp
def get_lib_entite():
    '''
    retourne un dictionnaire id/label 
    '''
    entite_ids = request.args.getlist('params')
    if not entite_ids:
        entites = Entite.query.all()
    else:
        entites = Entite.query.filter(Entite.id.in_(entite_ids)).all()
    return [{'id': item.id, 'label': item.label} for item in entites]



@routes.route('/entite', methods=['POST', 'PUT'])
@json_resp
def create_entite():
    '''
    cree une nouvelle entite
    '''
    data = request.json
    entite_type = data.pop('type_entite', 'entite')
    validateur = VALIDATEURS_E[entite_type]()
    parents = data.pop('parents', [])
    relations = data.pop('relations', [])
    try:
        entite_class = TYPES_E[entite_type]
        v_data, v_unhandled = validateur.validate(data)
        entite = entite_class(**v_data)
    except ValidationError as e:
        return {'errmsg': 'Données invalides', 'errors': e.error_list}, 400
    db.session.add(entite)
    db.session.flush()
    entite.parents = [p['id'] for p in parents if p]
    entite.relations = [r['id'] for r in relations if r]
    db.session.commit()
    return normalize(entite)



@routes.route('/entite/<id_entite>', methods=['POST', 'PUT'])
@json_resp
def update_entite(id_entite):
    '''
    met à jour une entite
    '''
    data = request.json
    entite_type = data.pop('type_entite', 'entite')
    try:
        validateur = VALIDATEURS_E[entite_type]()
        v_data, v_unhandled = validateur.validate(data)
    except ValidationError as e:
        return {'errmsg': 'Données invalides', 'errors': e.error_list}, 400
    parents = data.pop('parents', [])
    relations = data.pop('relations', [])
    entite = Entite.query.get(id_entite)
    if not entite:
        return {'errmsg': 'Donnée inexistante'}, 404
    if entite.type_entite != entite_type:
        return {'errmsg': 'Impossible de changer le type de la donnée'}, 400
    for attr, value in v_data.items():
        setattr(entite, attr, value)
    entite.parents = [p['id'] for p in parents if p]
    entite.relations = [r['id'] for r in relations if r]

    db.session.commit()
    return normalize(entite)


@routes.route('/entite/<id_entite>', methods=['DELETE'])
@json_resp
def delete_entite(id_entite):
    entite = Entite.query.get(id_entite)
    if not entite:
        return {'errmsg': 'Donnée inexistante'}, 404
    entite.delete_relations()
    db.session.delete(entite)
    db.session.commit()
    return []

#coding: utf8

'''
routes relatives à l'annuaire
'''
from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound
from .models import Entite, Commune, Correspondant, RelationEntite
from ..utils import normalize, json_resp, register_module
from server import db

routes = Blueprint('annuaire', __name__)

register_module('/annuaire', routes)


TYPES_E = {
        'entite': Entite,
        'commune': Commune,
        'correspondant': Correspondant,
        }

@routes.route('/entites')
@json_resp
def get_entites():
    '''
    retourne la liste des groupes
    '''
    entite_ids = request.args.getlist('params')
    if not entite_ids:
        entites = Entite.query.all()
    else:
        entites = get_entites_by_parent(entite_ids)
    return [normalize(e) for e in entites if isinstance(e, (Commune, Correspondant))]


def get_entites_by_parent(entite_ids):
    '''
    retourne une liste d'entites "enfants" de la liste d'ID fournie
    '''
    rels = RelationEntite.query.filter(RelationEntite.id_parent.in_(entite_ids)).all()
    all_ids = [item.id_enfant for item in rels]
    ids = set(filter(lambda x: all_ids.count(x)==len(entite_ids), all_ids))
    ids = ids | set(entite_ids)
    return Entite.query.filter(Entite.id.in_(ids)).order_by(Entite.type_entite).all()



@routes.route('/entite/<id_entite>')
@json_resp
def get_entite(id_entite):
    '''
    retourne une entite
    '''
    entite_type = request.args.get('type', 'entite')
    entite = TYPES_E[entite_type].query.get(id_entite)
    if not entite:
        return [], 404
    return normalize(entite)

@routes.route('/entites/<nom>')
@json_resp
def get_entite_nom(nom):
    '''
    retourne les entites correspondant à nom
    '''
    entite_type = request.args.get('type', 'entite')
    recherche = '%s%%' % '% '.join(nom.split())
    print(recherche)
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
    parents = data.pop('parents', [])
    entite_type = data.pop('type_entite', 'entite')
    entite = TYPES_E[entite_type](**data)
    db.session.add(entite)
    db.session.flush()
    print(parents)
    entite.parents = [p['id'] for p in parents if p]
    db.session.commit()
    return normalize(entite)



@routes.route('/entite/<id_entite>', methods=['POST', 'PUT'])
@json_resp
def update_entite(id_entite):
    '''
    met à jour une entite
    '''
    data = request.json
    parents = data.pop('parents', [])
    data.pop('label', '')
    entite_type = data.pop('type_entite', 'entite')
    entite = Entite.query.get(id_entite)
    if not entite:
        return [], 404
    for attr, value in data.items():
        setattr(entite, attr, value)
    entite.parents = [p['id'] for p in parents]
    db.session.commit()
    return normalize(entite)


@routes.route('/entite/<id_entite>', methods=['DELETE'])
@json_resp
def delete_entite(id_entite):
    entite = Entite.query.get(id_entite)
    if not entite:
        return [], 404
    entite.delete_relations()
    db.session.delete(entite)
    db.session.commit()
    return []

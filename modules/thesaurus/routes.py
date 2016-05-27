#coding: utf8

'''
Routes relatives au thésurus
'''

from flask import Blueprint
from . import models
from ..utils import normalize, json_resp


routes = Blueprint('th_routes', __name__)




def get_thesaurus(id_ref):
    '''
    effectue la requête sur la base de données en filtrant selon le
    parametre fourni.
    '''
    th_list = models.Thesaurus.query.filter(
            models.Thesaurus.id_ref==id_ref).all()
    out = []
    for item in th_list:
        out.append(normalize(item))
    return out


@routes.route('/services')
@json_resp
def get_services():
    '''
    retourne la liste des différents services
    '''
    return get_thesaurus(4)


@routes.route('/lieux')
@json_resp
def get_lieux():
    '''
    retourne la liste des différents lieux d'affectation
    '''
    return get_thesaurus(1)

@routes.route('/logements')
@json_resp
def get_logements():
    '''
    retourne la liste des options d'hébergement
    '''
    return get_thesaurus(10)

@routes.route('/contrats')
@json_resp
def get_contrats():
    '''
    retourne les différents types de contrats
    '''
    return get_thesaurus(14)

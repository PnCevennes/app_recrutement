#coding: utf8

'''
Routes relatives aux agents
'''
from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound
from .models import Agent
from ..utils import normalize, json_resp

routes = Blueprint('ag_routes', __name__)


@routes.route('/')
@json_resp
def get_agents():
    '''
    retourne la liste des agents en cours de recrutement
    '''
    ag_list = Agent.query.all()
    out = []
    for item in ag_list:
        out.append(normalize(item))
    if not out:
        return ['rien']
    return out



@routes.route('/<id_agent>', methods=['GET'])
@json_resp
def get_agent(id_agent):
    '''
    retourne l'agent identifié par `id_agent`
    '''
    try:
        agent = Agent.query.filter(models.Agent.id==id_agent).one()
        return normalize(agent)
    except NoResultFound as e:
        return [], 404



@routes.route('/', methods=['POST', 'PUT'])
@json_resp
def create_agent():
    '''
    crée un nouvel agent
    '''
    #TODO
    return []



@routes.route('/<id_agent>', methods=['POST', 'PUT'])
@json_resp
def update_agent(id_agent):
    '''
    met à jour un agent
    '''
    #TODO
    return []



@routes.route('/<id_agent>', methods=['DELETE'])
@json_resp
def delete_agent(id_agent):
    '''
    annule un recrutement en cours
    '''
    #TODO
    return []

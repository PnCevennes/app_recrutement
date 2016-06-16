#coding: utf8

'''
Routes relatives aux agents
'''
import datetime
from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound
from .models import Agent, AgentDetail
from ..thesaurus.models import Thesaurus
from ..utils import normalize, json_resp, send_mail, register_module, registered_funcs
from server import db

routes = Blueprint('recrutement', __name__)

register_module('/recrutement', routes)

check_auth = registered_funcs['check_auth']


@routes.route('/')
@json_resp
@check_auth(1, 2)
def get_agents():
    '''
    retourne la liste des agents en cours de recrutement
    '''
    today = datetime.date.today()
    get_old = request.args.get('old', False)
    if(get_old and get_old=='true'):
        qr = Agent.query.filter(Agent.arrivee>datetime.datetime(today.year, 1, 1))
    else:
        qr = Agent.query.filter(Agent.arrivee>today)

    ag_list = qr.order_by(db.asc(Agent.arrivee)).all()
    out = []
    for item in ag_list:
        out.append(normalize(item))
    if not out:
        return []
    return out



@routes.route('/<id_agent>', methods=['GET'])
@json_resp
def get_agent(id_agent):
    '''
    retourne l'agent identifié par `id_agent`
    '''
    agent = AgentDetail.query.get(id_agent)
    if not agent:
        return [], 404
    return normalize(agent)



@routes.route('/', methods=['POST', 'PUT'])
@json_resp
@check_auth(1, 2)
def create_agent():
    '''
    crée un nouvel agent
    '''
    try:
        ag = request.json
        ag['arrivee'] = datetime.datetime.strptime(
                ag['arrivee'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if 'depart' in ag and not (ag['depart'] == '' or ag['depart'] == None):
            ag['depart'] = datetime.datetime.strptime(
                    ag['depart'], '%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            ag.pop('depart', None)

        ag['materiel'] = [Thesaurus.query.get(item_id)
                for item_id in ag.get('materiel', [])]


        agent = AgentDetail(**ag)
        db.session.add(agent)
        db.session.commit()

        out = normalize(agent)
        send_mail(
            1,
            6,
            'Une nouvelle fiche de recrutement a été créée',
            '''
            La fiche de recrutement de %s %s a été créée le %s.
            Vous pouvez vous connecter http://192.168.10.10/recrutement/app.htm pour voir les détails de cette fiche.
            ''' % (
                agent.prenom,
                agent.nom,
                datetime.datetime.today().strftime('%d/%m/%Y'),
                )
            )

        return out

    except Exception as e:
        return [], 400



@routes.route('/<id_agent>', methods=['POST', 'PUT'])
@json_resp
@check_auth(1, 2)
def update_agent(id_agent):
    '''
    met à jour un agent
    '''
    try:
        ag = request.json
        ag['arrivee'] = datetime.datetime.strptime(ag['arrivee'], '%Y-%m-%dT%H:%M:%S.%fZ') 
        if 'depart' in ag and not (ag['depart'] == '' or ag['depart'] == None):
            ag['depart'] = datetime.datetime.strptime(ag['depart'], '%Y-%m-%dT%H:%M:%S.%fZ') 
        else:
            ag.pop('depart')
        agent = AgentDetail.query.get(id_agent)
        if not agent:
            return [], 404

        ag['materiel'] = [Thesaurus.query.get(item_id)
                for item_id in ag.get('materiel', [])]


        for col in ag:
            setattr(agent, col, ag[col])

        db.session.commit()

        out = normalize(agent)
        send_mail(
            1,
            6,
            'Une fiche de recrutement a été modifiée',
             '''
            La fiche de recrutement de %s %s a été modifiée le %s.
            Vous pouvez vous connecter à http://192.168.10.10/recrutement/app.htm pour voir les détails de cette fiche.
            ''' % (
                agent.prenom,
                agent.nom,
                datetime.datetime.today().strftime('%d/%m/%Y'),
                )
            )
        return out
    except Exception as e:
        print(e)
        return [], 400



@routes.route('/<id_agent>', methods=['DELETE'])
@json_resp
@check_auth(1, 2)
def delete_agent(id_agent):
    '''
    annule un recrutement en cours
    '''
    agent = AgentDetail.query.get(id_agent)
    if not agent:
        return [], 404
    db.session.delete(agent)
    db.session.commit()
    send_mail(
        1,
        6,
        'Une fiche de recrutement a été supprimée',
        '''
        La fiche de recrutement de %s %s a été supprimée le %s.
        Vous pouvez vous connecter à http://192.168.10.10/recrutement/app.htm pour voir la liste des recrutements en cours.
        ''' % (
            agent.prenom,
            agent.nom,
            datetime.datetime.today().strftime('%d/%m/%Y')
            )
        )
    return []

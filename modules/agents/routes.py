#coding: utf8

'''
Routes relatives aux agents
'''
import datetime
from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound
from .models import Agent, AgentDetail
from ..utils import normalize, json_resp, send_mail
from server import db

routes = Blueprint('ag_routes', __name__)


@routes.route('/')
@json_resp
def get_agents():
    '''
    retourne la liste des agents en cours de recrutement
    '''
    get_old = request.args.get('old', False)
    if(get_old and get_old=='true'):
        qr = Agent.query
    else:
        qr = Agent.query.filter(Agent.arrivee>datetime.date.today())

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
    return normalize(agent, Agent)



@routes.route('/', methods=['POST', 'PUT'])
@json_resp
def create_agent():
    '''
    crée un nouvel agent
    '''
    try:
        ag = request.json
        ag['arrivee'] = datetime.datetime.strptime(ag['arrivee'], '%Y-%m-%dT%H:%M:%S.%fZ') 
        ag['depart'] = datetime.datetime.strptime(ag['depart'], '%Y-%m-%dT%H:%M:%S.%fZ') 
        agent = AgentDetail(**ag)
        db.session.add(agent)
        db.session.commit()

        send_mail(
            '[recrutement] Une nouvelle fiche de recrutement a été créée',
            '''
            La fiche de recrutement de %s %s a été crée le %s.
            Vous pouvez vous connecter à <serveur>%s pour voir les détails de cette fiche.
            ''' % (
                agent.prenom,
                agent.nom,
                datetime.datetime.today().strftime('%d/%m/%Y'),
                agent.id
                )
            )

        return normalize(agent)
    except Exception as e:
        print(e)
        return [], 400



@routes.route('/<id_agent>', methods=['POST', 'PUT'])
@json_resp
def update_agent(id_agent):
    '''
    met à jour un agent
    '''
    try:
        ag = request.json
        ag['arrivee'] = datetime.datetime.strptime(ag['arrivee'], '%Y-%m-%dT%H:%M:%S.%fZ') 
        ag['depart'] = datetime.datetime.strptime(ag['depart'], '%Y-%m-%dT%H:%M:%S.%fZ') 
        agent = AgentDetail.query.get(id_agent)
        if not agent:
            return [], 404
        for col in ag:
            setattr(agent, col, ag[col])
        db.session.commit()

        app = get_app()

        send_mail(
            '[recrutement] Une fiche de recrutement a été modifiée',
             '''
            La fiche de recrutement de %s %s a été modifiée le %s.
            Vous pouvez vous connecter à <serveur>%s pour voir les détails de cette fiche.
            ''' % (
                agent.prenom,
                agent.nom,
                datetime.datetime.today().strftime('%d/%m/%Y'),
                agent.id
                )
            )
        with app.app_context():
            mail.send(msg)

        return normalize(agent)
    except Exception as e:
        print(e)
        return [], 400



@routes.route('/<id_agent>', methods=['DELETE'])
@json_resp
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
        'Une fiche de recrutement a été supprimée',
        '''
        La fiche de recrutement de %s %s a été supprimée le %s.
        Vous pouvez vous connecter à <serveur> pour voir la liste des recrutements en cours.
        ''' % (
            agent.prenom,
            agent.nom,
            datetime.datetime.today().strftime('%d/%m/%Y')
            )
        )
    return []

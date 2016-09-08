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
def get_agents():
    '''
    retourne la liste des agents en cours de recrutement
    '''
    today = datetime.date.today()
    try:
        annee = request.args.get('annee', False)
        if not annee:
            annee = today.year
        else:
            annee = int(annee)
    except ValueError:
        return [], 400
    annee_deb = datetime.date(annee, 1, 1)
    annee_fin = datetime.date(annee, 12, 31)
    qr = Agent.query.filter(Agent.arrivee.between(annee_deb, annee_fin))

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

        ag['meta_create'] = datetime.datetime.now()

        agent = AgentDetail(**ag)
        db.session.add(agent)
        db.session.commit()

        out = normalize(agent)
        send_mail(
            3,
            6,
            'Nouvelle fiche de recrutement',
            '''
            La fiche de recrutement de %s %s a été créée le %s.
            Vous pouvez vous connecter sur http://192.168.10.10/recrutement/app.htm#/recrutement?annee=%s&agent=%s pour voir les détails de cette fiche.
            ''' % (
                agent.prenom,
                agent.nom,
                datetime.datetime.today().strftime('%d/%m/%Y'),
                agent.arrivee.year,
                agent.id
                )
            )

        return out

    except Exception as e:
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
        ag['meta_create'] = datetime.datetime.strptime(ag['meta_create'], '%Y-%m-%dT%H:%M:%S.%fZ') 
        if 'depart' in ag and not (ag['depart'] == '' or ag['depart'] == None):
            ag['depart'] = datetime.datetime.strptime(ag['depart'], '%Y-%m-%dT%H:%M:%S.%fZ') 
        else:
            ag.pop('depart')
        agent = AgentDetail.query.get(id_agent)
        if not agent:
            return [], 404

        ag['materiel'] = [Thesaurus.query.get(item_id)
                for item_id in ag.get('materiel', [])]

        ag['meta_update'] = datetime.datetime.now()

        for col in ag:
            setattr(agent, col, ag[col])

        db.session.commit()

        out = normalize(agent)
        send_mail(
            3,
            6,
            "Modification d'une fiche de recrutement",
             '''
            La fiche de recrutement de %s %s a été modifiée le %s.
            Vous pouvez vous connecter à http://192.168.10.10/recrutement/app.htm#/recrutement?annee=%s&agent=%s pour voir les détails de cette fiche.
            ''' % (
                agent.prenom,
                agent.nom,
                datetime.datetime.today().strftime('%d/%m/%Y'),
                agent.arrivee.year,
                agent.id
                )
            )
        return out
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
        3,
        6,
        "Suppression d'une fiche de recrutement",
        '''
        La fiche de recrutement de %s %s a été supprimée le %s.
        Vous pouvez vous connecter à http://192.168.10.10/recrutement/app.htm#/recrutement pour voir la liste des recrutements en cours.
        ''' % (
            agent.prenom,
            agent.nom,
            datetime.datetime.today().strftime('%d/%m/%Y')
            )
        )
    return []

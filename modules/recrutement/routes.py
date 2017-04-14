#coding: utf8

'''
Routes relatives aux agents
'''
import datetime
from flask import Blueprint, request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from models import Fichier
from modules.thesaurus.models import Thesaurus
from modules.utils import normalize, json_resp, send_mail, register_module, registered_funcs, delete_file
from .models import Agent, AgentDetail, RelAgentFichier

db = SQLAlchemy()

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

        ag['materiel'] = [db.session.query(Thesaurus).get(item_id)
                for item_id in ag.get('materiel', [])]


        ag['fichiers'] = [db.session.query(Fichier).get(fich['id'])
                for fich in ag.get('fichiers', [])]


        ag['meta_create'] = datetime.datetime.now()
        notif = ag.pop('ctrl_notif', False)

        agent = AgentDetail(**ag)
        db.session.add(agent)
        db.session.commit()

        out = normalize(agent)
        if notif:
            send_mail(
                3,
                6,
                'Nouvelle fiche de recrutement',
                '''
                La fiche de recrutement de %s %s a été créée le %s.
                Vous pouvez vous connecter sur http://devel.pnc.int/outils/#/recrutement?annee=%s&agent=%s pour voir les détails de cette fiche.
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
        print(type(e))
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
        ag['meta_create'] = datetime.datetime.strptime(ag['meta_create'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if 'depart' in ag and not (ag['depart'] == '' or ag['depart'] == None):
            ag['depart'] = datetime.datetime.strptime(ag['depart'], '%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            ag.pop('depart')
        agent = db.session.query(AgentDetail).get(id_agent)
        if not agent:
            return [], 404

        ag['materiel'] = [db.session.query(Thesaurus).get(item_id)
                for item_id in ag.get('materiel', [])]
        print(ag['materiel'])

        ag['fichiers'] = [db.session.query(Fichier).get(fich['id'])
                for fich in ag.get('fichiers', [])]

        ag['meta_update'] = datetime.datetime.now()
        notif = ag.pop('ctrl_notif', False)

        for col in ag:
            setattr(agent, col, ag[col])

        db.session.commit()

        out = normalize(agent)
        if notif:
            send_mail(
                3,
                6,
                "Modification d'une fiche de recrutement",
                '''
                La fiche de recrutement de %s %s a été modifiée le %s.
                Vous pouvez vous connecter à http://devel.pnc.int/outils/#/recrutement?annee=%s&agent=%s pour voir les détails de cette fiche.
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
    agent = db.session.query(AgentDetail).get(id_agent)
    if not agent:
        return [], 404
    rels_fichiers = db.session.query(RelAgentFichier).filter(
            RelAgentFichier.id_agent==id_agent).all()
    for rel in rels_fichiers:
        delete_file(rel.id_fichier)
        db.session.delete(rel)
    db.session.delete(agent)
    db.session.commit()
    send_mail(
        3,
        6,
        "Suppression d'une fiche de recrutement",
        '''
        La fiche de recrutement de %s %s a été supprimée le %s.
        Vous pouvez vous connecter à http://devel.pnc.int/outils/#/recrutement pour voir la liste des recrutements en cours.
        ''' % (
            agent.prenom,
            agent.nom,
            datetime.datetime.today().strftime('%d/%m/%Y')
            )
        )
    return []

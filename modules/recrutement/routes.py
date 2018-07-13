'''
Routes relatives aux agents
'''

import datetime

from flask import Blueprint, request, Response
from werkzeug.datastructures import Headers

from server import db as _db
from models import Fichier
from routes import upload_file, get_uploaded_file, delete_uploaded_file
from modules.thesaurus.models import Thesaurus
from modules.utils import (
        json_resp,
        send_mail,
        register_module
        )
from .models import (
        Agent,
        AgentDetail,
        AgentSerializer,
        AgentDetailSerializer,
        RelAgentFichier)
from serialize_utils import ValidationError


routes = Blueprint('recrutement', __name__)

register_module('/recrutement', routes)


def format_csv(data, sep='", "'):
    _fields = [
            'id',
            'nom',
            'prenom',
            'intitule_poste',
            'service_id',
            'arrivee',
            'depart',
            'desc_mission',
            'type_contrat',
            'lieu',
            'categorie',
            'temps_travail',
            'temps_travail_autre'
            ]
    out = ['%s' % sep.join(_fields)]
    for item in data:
        try:
            line = AgentDetailSerializer(item).serialize(_fields)
        except ValidationError as e:
            print(e.errors)

        if line['type_contrat']:
            line['type_contrat'] = (
                    _db.session.query(Thesaurus)
                    .get(line['type_contrat'])
                    .label)
        else:
            line['type_contrat'] = None
        if line['lieu']:
            line['lieu'] = (
                    _db.session.query(Thesaurus)
                    .get(line['lieu'])
                    .label)
        else:
            line['lieu'] = None
        if line['service_id']:
            line['service_id'] = (
                    _db.session.query(Thesaurus)
                    .get(line['service_id'])
                    .label)
        else:
            line['service_id'] = None
        if line['categorie']:
            line['categorie'] = (
                    _db.session.query(Thesaurus)
                    .get(line['categorie'])
                    .label)
        else:
            line['categorie'] = None
        if line['temps_travail']:
            line['temps_travail'] = (
                    _db.session.query(Thesaurus)
                    .get(line['temps_travail'])
                    .label)
        else:
            line['temps_travail'] = None
        out.append('%s' % sep.join([
            str(col) if col else ''
            for col in line.values()]))
    headers = Headers()
    headers.add('Content-Type', 'text/plain')
    headers.add('Content-Disposition', 'attachment', filename='export.csv')
    return Response(('\n'.join(out)), headers=headers)


@routes.route('/')
@json_resp
def get_agents():
    '''
    retourne la liste des agents en cours de recrutement
    '''
    today = datetime.date.today()
    _format = request.args.get('format', 'dict')
    try:
        annee = request.args.get('annee', False)
        if not annee:
            annee = today.year
        else:
            annee = int(annee)
    except ValueError:
        return [], 400
    try:
        annee_deb = datetime.date(annee, 1, 1)
        annee_fin = datetime.date(annee, 12, 31)
        if _format == 'dict':
            qr = Agent.query.filter(Agent.arrivee.between(annee_deb, annee_fin))
        else:
            qr = AgentDetail.query.filter(AgentDetail.arrivee.between(annee_deb, annee_fin))

        ag_list = qr.order_by(_db.asc(Agent.arrivee)).all()
        if _format == 'csv':
            return format_csv(ag_list, ';')
        if _format == 'tsv':
            return format_csv(ag_list, "\t")
        else:
            return [AgentSerializer(res).serialize() for res in ag_list]
    except Exception:
        import traceback
        return [{'msg': traceback.format_exc()}], 400


@routes.route('/<id_agent>', methods=['GET'])
@json_resp
def get_agent(id_agent):
    '''
    retourne l'agent identifié par `id_agent`
    '''
    agent = AgentDetail.query.get(id_agent)
    if not agent:
        return [], 404
    return AgentDetailSerializer(agent).serialize()


@routes.route('/', methods=['POST', 'PUT'])
@json_resp
def create_agent():
    '''
    crée un nouvel agent
    '''
    try:
        ag = request.json
        ag['arrivee'] = datetime.datetime.strptime(
                ag['arrivee'], '%Y-%m-%d')
        if 'depart' in ag and not (ag['depart'] == '' or ag['depart'] == None):  # noqa
            ag['depart'] = datetime.datetime.strptime(
                    ag['depart'], '%Y-%m-%d')
        else:
            ag.pop('depart', None)

        ag['materiel'] = [
                _db.session.query(Thesaurus).get(item_id)
                for item_id in ag.get('materiel', [])]

        ag['fichiers'] = [
                _db.session.query(Fichier).get(fich['id'])
                for fich in ag.get('fichiers', [])]
        ag['notif_list'] = ','.join(ag['notif_list'])
        ag['meta_create'] = datetime.datetime.now()
        notif = ag.pop('ctrl_notif', False)

        agent = AgentDetail(**ag)
        _db.session.add(agent)
        _db.session.commit()

        out = AgentDetailSerializer(agent).serialize()
        if notif:
            send_mail(
                ['tizoutis-recrutement', 'admin-tizoutis'],
                'Nouvelle fiche de recrutement : %s %s' % (
                    agent.prenom or '',
                    agent.nom
                    ),
                '''
                La fiche de recrutement de %s %s a été créée le %s.
                Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/recrutement?annee=%s&fiche=%s pour voir les détails de cette fiche.
                ''' % (
                    agent.prenom or '',
                    agent.nom,
                    datetime.datetime.today().strftime('%d/%m/%Y'),
                    agent.arrivee.year,
                    agent.id
                    ),
                add_dests=ag['notif_list'].split(',')
                )

        return out

    except Exception:
        import traceback
        return [{'msg': traceback.format_exc()}], 400


@routes.route('/<id_agent>', methods=['POST', 'PUT'])
@json_resp
def update_agent(id_agent):
    '''
    met à jour un agent
    '''
    try:
        ag = request.json
        ag['notif_list'] = ','.join(ag['notif_list'])
        ag['arrivee'] = datetime.datetime.strptime(
                ag['arrivee'], '%Y-%m-%d')
        ag['meta_create'] = datetime.datetime.strptime(
                ag['meta_create'], '%Y-%m-%d')
        if 'depart' in ag and not (ag['depart'] == '' or ag['depart'] == None):  # noqa
            ag['depart'] = datetime.datetime.strptime(
                    ag['depart'], '%Y-%m-%d')
        else:
            ag.pop('depart')
        agent = _db.session.query(AgentDetail).get(id_agent)
        if not agent:
            return [], 404

        ag['materiel'] = [
                _db.session.query(Thesaurus).get(item_id)
                for item_id in ag.get('materiel', [])]

        ag['fichiers'] = [
                _db.session.query(Fichier).get(fich['id'])
                for fich in ag.get('fichiers', [])]

        ag['meta_update'] = datetime.datetime.now()
        notif = ag.pop('ctrl_notif', False)

        for col in ag:
            setattr(agent, col, ag[col])

        _db.session.commit()

        out = AgentDetailSerializer(agent).serialize()
        if notif:
            send_mail(
                ['tizoutis-recrutement', 'admin-tizoutis'],
                "Modification d'une fiche de recrutement : %s %s" % (
                    agent.prenom or '',
                    agent.nom
                    ),
                '''
                La fiche de recrutement de %s %s a été modifiée le %s.
                Vous pouvez vous connecter à http://tizoutis.pnc.int/#/recrutement?annee=%s&fiche=%s pour voir les détails de cette fiche.
                ''' % (
                    agent.prenom or '',
                    agent.nom,
                    datetime.datetime.today().strftime('%d/%m/%Y'),
                    agent.arrivee.year,
                    agent.id
                    ),
                add_dests=ag['notif_list'].split(',')
                )

        return out
    except Exception as exc:
        import traceback
        print(exc)
        print(traceback.format_exc())
        return [{'msg': traceback.format_exc()}], 400


@routes.route('/<id_agent>', methods=['DELETE'])
@json_resp
def delete_agent(id_agent):
    '''
    annule un recrutement en cours
    '''
    agent = _db.session.query(AgentDetail).get(id_agent)
    if not agent:
        return [], 404
    rels_fichiers = _db.session.query(RelAgentFichier).filter(
            RelAgentFichier.id_agent == id_agent).all()
    for rel in rels_fichiers:
        delete_uploaded_file(rel.id_fichier, _db)
        #_db.session.delete(rel)
    _db.session.delete(agent)
    _db.session.commit()
    send_mail(
        ['tizoutis-recrutement', 'admin-tizoutis'],
        "Suppression d'une fiche de recrutement : %s %s" % (
            agent.prenom or '',
            agent.nom
            ),
        '''
        La fiche de recrutement de %s %s a été supprimée le %s.
        Vous pouvez vous connecter à http://tizoutis.pnc.int/#/recrutement pour voir la liste des recrutements en cours.
        ''' % (
            agent.prenom or '',
            agent.nom,
            datetime.datetime.today().strftime('%d/%m/%Y')
            ),
        add_dests=agent.notif_list.split(',')
        )
    return []


@routes.route('/upload', methods=['POST'])
@json_resp
def v_recr_upload_file():
    if 'fichier' not in request.files:
        return {}, 400
    return upload_file(request.files['fichier'])


@routes.route('/upload/<file_uri>', methods=['GET'])
def v_recr_get_uploaded_file(file_uri):
    return get_uploaded_file(file_uri)


@routes.route('/upload/<fileid>', methods=['DELETE'])
@json_resp
def v_recr_delete_uploaded_file(fileid):
    rels_fichiers = _db.session.query(RelAgentFichier).filter(
            RelAgentFichier.id_fichier == fileid).all()
    for rel in rels_fichiers:
        _db.session.delete(rel)
        _db.session.commit()
    return delete_uploaded_file(fileid, db=_db)

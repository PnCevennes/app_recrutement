'''
Routes relatives aux agents
'''

import datetime

from flask import Blueprint, request, Response
from werkzeug.datastructures import Headers

from server import db as _db
from core.models import Fichier, prepare_fichiers
from core.routes import upload_file, get_uploaded_file, delete_uploaded_file
from core.thesaurus.models import Thesaurus
from core.utils import (
        json_resp,
        send_mail,
        csv_response,
        register_module,
        registered_funcs
        )
from core.utils.serialize import load_ref, ValidationError
from .models import (
        Agent,
        AgentDetail,
        RelAgentFichier)
from .serializers import (
        AgentSerializer,
        AgentDetailSerializer
        )


AgentDetailSerializer.fichiers.preparefn = prepare_fichiers(_db)


routes = Blueprint('recrutement', __name__)

register_module('/recrutement', routes)

check_auth = registered_funcs['check_auth']

csv_fields = [
        'id',
        'nom',
        'prenom',
        'intitule_poste',
        (
            'service_id',
            load_ref(_db, Thesaurus, 'label')
        ),
        'arrivee',
        'depart',
        'desc_mission',
        (
            'type_contrat',
            load_ref(_db, Thesaurus, 'label')
        ),
        (
            'service_id',
            load_ref(_db, Thesaurus, 'label')
        ),
        (
            'lieu',
            load_ref(_db, Thesaurus, 'label')
        ),
        (
            'categorie',
            load_ref(_db, Thesaurus, 'label')
        ),
        (
            'temps_travail',
            load_ref(_db, Thesaurus, 'label')
        ),
        'temps_travail_autre'
        ]


@routes.route('/')
@json_resp
@check_auth()
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
            return csv_response(AgentDetailSerializer.export_csv(ag_list, fields=csv_fields), filename='recrutement.csv') 
            return format_csv(ag_list, ';')
        else:
            return [AgentSerializer(res).serialize() for res in ag_list]
    except Exception:
        import traceback
        return [{'msg': traceback.format_exc()}], 400


@routes.route('/<id_agent>', methods=['GET'])
@json_resp
@check_auth()
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
@check_auth()
def create_agent():
    '''
    crée un nouvel agent
    '''
    try:
        ag = request.json
        ag.pop('meta_create')
        ag['materiel'] = [
                _db.session.query(Thesaurus).get(item_id)
                for item_id in ag.get('materiel', [])]
        notif = ag.pop('ctrl_notif', False)

        # agent = AgentDetail(**ag)
        agent = AgentDetail()
        AgentDetailSerializer(agent).populate(ag)
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
                add_dests=ag['notif_list']
                )

        return out

    except Exception:
        import traceback
        return [{'msg': traceback.format_exc()}], 400


@routes.route('/<id_agent>', methods=['POST', 'PUT'])
@json_resp
@check_auth()
def update_agent(id_agent):
    '''
    met à jour un agent
    '''
    try:
        ag = request.json
        agent = _db.session.query(AgentDetail).get(id_agent)
        if not agent:
            return [], 404

        ag['materiel'] = [
                _db.session.query(Thesaurus).get(item_id)
                for item_id in ag.get('materiel', [])]

        ag['meta_update'] = datetime.datetime.now()
        notif = ag.pop('ctrl_notif', False)

        AgentDetailSerializer(agent).populate(ag)

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
                add_dests=ag['notif_list']
                )

        return out
    except Exception as exc:
        import traceback
        print(exc)
        print(traceback.format_exc())
        return [{'msg': traceback.format_exc()}], 400


@routes.route('/<id_agent>', methods=['DELETE'])
@json_resp
@check_auth()
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

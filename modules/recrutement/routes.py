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
from core.utils.rtf import render_rtf
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
    'referent',
    'temps_travail_autre',
    'residence_administrative',
    (
        'logement',
        load_ref(_db, Thesaurus, 'label')
    ),
    'convention_signee',
    'gratification',
    'bureau',
    'observations'
]


def get_agents_annee(annee_deb, annee_fin, frmt='dict'):
    '''
    Retourne la liste des agents recrutés dans l'année
    '''
    if frmt == 'dict':
        klass = Agent
    else:
        klass = AgentDetail
    qr = klass.query.filter(klass.arrivee.between(annee_deb, annee_fin))
    return qr.order_by(_db.asc(Agent.arrivee)).all()


def get_agents_presents(annee_deb, annee_fin, frmt='dict'):
    '''
    Retourne la liste des agents présents au cours de l'année
    '''
    if frmt == 'dict':
        klass = Agent
    else:
        klass = AgentDetail
    qr = klass.query.filter(
        _db.and_(
            _db.or_(
                klass.depart >= annee_deb,
                klass.depart == None  # noqa
            ),
            klass.arrivee <= annee_fin
        )
    )
    return qr.order_by(_db.asc(klass.arrivee)).all()


@routes.route('/')
@json_resp
@check_auth()
def get_agents():
    '''
    retourne la liste des agents en cours de recrutement
    '''
    today = datetime.date.today()
    _format = request.args.get('format', 'dict')
    add_prev_years = request.args.get('add_prev_years', False)
    if add_prev_years == 'false':
        add_prev_years = False
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
        if not add_prev_years:
            ag_list = get_agents_annee(annee_deb, annee_fin, _format)
        else:
            ag_list = get_agents_presents(annee_deb, annee_fin, _format)
        if _format == 'csv':
            return csv_response(
                AgentDetailSerializer.export_csv(
                    ag_list,
                    fields=csv_fields
                ),
                filename='recrutement.csv'
            )
        else:
            return [AgentSerializer(res).dump() for res in ag_list]
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
    _format = request.args.get('format', 'dict')
    agent = AgentDetail.query.get(id_agent)
    if not agent:
        return [], 404
    if _format == 'document':
        data = AgentDetailSerializer(agent).dump(csv_fields)
        return render_rtf(
                'recrutement_%s_%s' % (
                    agent.nom.encode('ascii', errors='replace').decode('utf8'),
                    agent.prenom.encode('ascii', errors='replace').decode('utf8')
                    ),
                'templates/recrutement/template_recrutement.rtf',
                data)
    return AgentDetailSerializer(agent).dump()


@routes.route('/', methods=['POST', 'PUT'])
@json_resp
@check_auth()
def create_agent():
    '''
    crée un nouvel agent
    '''
    try:
        ag = request.json
        ag['materiel'] = [
            _db.session.query(Thesaurus).get(item_id)
            for item_id in ag.get('materiel', [])
        ]
        notif = ag.pop('ctrl_notif', False)

        # agent = AgentDetail(**ag)
        agent = AgentDetail()
        AgentDetailSerializer(agent).load(ag)
        _db.session.add(agent)
        _db.session.commit()

        out = AgentDetailSerializer(agent).dump()
        if notif:
            send_mail(
                ['tizoutis-recrutement', 'admin-tizoutis'],
                'Nouvelle fiche de recrutement : %s %s' % (
                    agent.prenom or '',
                    agent.nom
                ),
                '''
                La fiche de recrutement de %s %s a été créée le %s.
                Vous pouvez vous connecter sur
                http://tizoutis.pnc.int/#/recrutement?annee=%s&fiche=%s
                pour voir les détails de cette fiche.
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
            for item_id in ag.get('materiel', [])
        ]

        ag['meta_update'] = str(datetime.date.today())
        notif = ag.pop('ctrl_notif', False)

        AgentDetailSerializer(agent).load(ag)

        _db.session.commit()

        out = AgentDetailSerializer(agent).dump()
        if notif:
            send_mail(
                ['tizoutis-recrutement', 'admin-tizoutis'],
                "Modification d'une fiche de recrutement : %s %s" % (
                    agent.prenom or '',
                    agent.nom
                ),
                '''
                La fiche de recrutement de %s %s a été modifiée le %s.
                Vous pouvez vous connecter à
                http://tizoutis.pnc.int/#/recrutement?annee=%s&fiche=%s
                pour voir les détails de cette fiche.
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
    """
    rels_fichiers = _db.session.query(RelAgentFichier).filter(
        RelAgentFichier.id_agent == id_agent
    ).all()
    for rel in rels_fichiers:
        delete_uploaded_file(rel.id_fichier, _db)
    """
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
        Vous pouvez vous connecter à
        http://tizoutis.pnc.int/#/recrutement
        pour voir la liste des recrutements en cours.
        ''' % (
            agent.prenom or '',
            agent.nom,
            datetime.datetime.today().strftime('%d/%m/%Y')
        ),
        add_dests=agent.notif_list.split(',')
    )
    return []

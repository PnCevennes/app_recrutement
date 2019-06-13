'''
Routes relatives aux demandes d'intervention
'''
import datetime

from flask import Blueprint, request, Response
from werkzeug.datastructures import Headers
from sqlalchemy.exc import InvalidRequestError

from server import db as _db
from core.models import Fichier, prepare_fichiers, get_chrono, amend_chrono
from core.thesaurus.models import Thesaurus
from core.utils import (
        json_resp,
        csv_response,
        send_mail,
        register_module,
        registered_funcs
        )
from .models import Demande

from .serializers import (
        DemandeSerializer,
        DemandeFullSerializer)
from core.utils.serialize import load_ref, ValidationError


DemandeFullSerializer.dem_fichiers.preparefn = prepare_fichiers(_db)
DemandeFullSerializer.rea_fichiers.preparefn = prepare_fichiers(_db)


routes = Blueprint('interventions', __name__)

register_module('/interventions', routes)

check_auth = registered_funcs['check_auth']


csv_fields = [
        'id',
        'num_intv',
        (
            'dem_objet',
            load_ref(_db, Thesaurus, 'label')
        ),
        'dem_date',
        (
            'dem_localisation',
            load_ref(_db, Thesaurus, 'label')
        ),
        'dem_details',
        (
            'dmdr_service',
            load_ref(_db, Thesaurus, 'label')
        ),
        'dem_delai',
        'dem_loc_commune',
        'dem_loc_libelle',
        'rea_duree',
        'dmdr_contact_nom',
        'plan_commentaire',
        'plan_date',
        'rea_date',
        'rea_nb_agents',
        'rea_commentaire']


def get_demande_encours(annee_deb, annee_fin):
    return (
            _db.session.query(Demande)
            .filter(
                _db.and_(
                    Demande.dem_date <= annee_fin,
                    _db.or_(
                        Demande.rea_date == None,
                        Demande.rea_date >= annee_deb
                    )
                )
            )
            .all())

def get_demande_annee(annee_deb, annee_fin):
    return _db.session.query(Demande).filter(Demande.dem_date.between(annee_deb, annee_fin)).all()


@routes.route('/', methods=['GET'])
@json_resp
@check_auth()
def get_interventions():
    """
    retourne la liste des demandes d'intervention
    """

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
            results = get_demande_annee(annee_deb, annee_fin)
        else:
            results = get_demande_encours(annee_deb, annee_fin)

        print(len(results))
        if _format == 'csv':
            return csv_response(DemandeFullSerializer.export_csv(results, fields=csv_fields), filename='interventions.csv')
        else:
            return [DemandeSerializer(res).serialize() for res in results]
    except Exception:
        import traceback
        return [{'msg': traceback.format_exc()}], 400


@routes.route('/<id_intervention>', methods=['GET'])
@json_resp
@check_auth()
def get_one_intervention(id_intervention):
    """
    retourne une demande d'intervention identifiée par id_intervention
    """
    result = _db.session.query(Demande).get(id_intervention)
    return DemandeFullSerializer(result).serialize()


@routes.route('/', methods=['POST', 'PUT'])
@json_resp
@check_auth()
def create_intervention():
    """
    crée une nouvelle demande d'intervention
    """
    dem = request.json
    dem['dem_date'] = datetime.date.today()
    ref_chrono = '{}INTV'.format(str(dem['dem_date'].year)[2:4])

    demande = Demande()
    try:
        chrono = get_chrono(ref_chrono)
        dem['num_intv'] = chrono
        DemandeFullSerializer(demande).populate(dem)
        _db.session.add(demande)
        _db.session.commit()

        dem_loc = _db.session.query(Thesaurus).get(demande.dem_localisation).label
        dem_objet = _db.session.query(Thesaurus).get(demande.dem_objet).label
        send_mail(
                ['tizoutis-interventions', 'admin-tizoutis'],
                "Création de la demande d'intervention n°%s - %s %s" % (
                    demande.id,
                    dem_objet,
                    dem_loc
                    ),
                '''
                Une nouvelle demande d'intervention a été créée.
                Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions?fiche=%s pour voir les détails de cette demande.
                ''' % demande.id,
                add_dests=demande.dmdr_contact_email.split(','),
                sendername='interventions'
                )

        return {'id': demande.id}
    except ValidationError as e:
        amend_chrono(ref_chrono)
        return e.errors, 400


@routes.route('/<id_intervention>', methods=['POST', 'PUT'])
@json_resp
@check_auth()
def update_intervention(id_intervention):
    """
    met à jour une demande d'intervention identifée par id_intervention
    """
    dem = request.json

    demande = _db.session.query(Demande).get(id_intervention)
    try:
        DemandeFullSerializer(demande).populate(dem)
        #_db.session.add(demande)
        _db.session.commit()

        dem_loc = _db.session.query(Thesaurus).get(demande.dem_localisation).label
        dem_objet = _db.session.query(Thesaurus).get(demande.dem_objet).label

        send_mail(
                ['tizoutis-interventions', 'admin-tizoutis'],
                "Mise à jour de la demande d'intervention n°%s - %s %s" % (
                    demande.id,
                    dem_objet,
                    dem_loc
                    ),
                '''
                La demande d'intervention n°%s a été modifiée.
                Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions?fiche=%s pour voir les détails de cette demande.
                ''' % (demande.id, demande.id),
                add_dests=demande.dmdr_contact_email.split(','),
                sendername='interventions'
                )

        return {'id': demande.id}
    except ValidationError as e:
        return e.errors, 400
    except:
        import traceback
        print(traceback.format_exc())
        _db.session.rollback()
        return {}, 400


@routes.route('/<id_intervention>', methods=['DELETE'])
@json_resp
@check_auth(['tizoutis-interventions'])
def delete_intervention(id_intervention):
    """
    supprime une demande d'intervention identifiée par id_intervention
    """
    demande = _db.session.query(Demande).get(id_intervention)
    _db.session.delete(demande)
    _db.session.commit()

    dem_loc = _db.session.query(Thesaurus).get(demande.dem_localisation).label
    dem_objet = _db.session.query(Thesaurus).get(demande.dem_objet).label

    send_mail(
            ['tizoutis-interventions', 'admin-tizoutis'],
            "Annulation de la demande d'intervention n°%s - %s %s" % (
                    demande.id,
                    dem_objet,
                    dem_loc
                    ),
            '''
            La demande d'intervention n°%s a été annulée.
            Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions/ pour voir la liste des demandes en cours.
            ''',
            add_dests=demande.dmdr_contact_email.split(','),
            sendername='interventions')

    return {'id': demande.id}

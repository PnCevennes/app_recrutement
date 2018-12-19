'''
Routes relatives aux demandes de travaux sur batiments
'''

import datetime

from flask import Blueprint, request, Response
from werkzeug.datastructures import Headers

from server import db as _db
from core.models import Fichier, prepare_fichiers
from core.thesaurus.models import Thesaurus
from core.refgeo.models import RefGeoCommunes, RefGeoBatiment
from core.utils import (
        json_resp,
        csv_response,
        send_mail,
        register_module,
        registered_funcs
        )
from core.utils.serialize import ValidationError
from .models import TravauxBatiment

from .serializers import (
        TravauxBatimentSerializer,
        TravauxBatimentFullSerializer)


TravauxBatimentFullSerializer.dem_fichiers.preparefn = prepare_fichiers(_db)
TravauxBatimentFullSerializer.plan_fichiers.preparefn = prepare_fichiers(_db)
TravauxBatimentFullSerializer.rea_fichiers.preparefn = prepare_fichiers(_db)


routes = Blueprint('travaux_batiments', __name__)

register_module('/travaux_batiments', routes)

check_auth = registered_funcs['check_auth']

csv_fields = [
        'id',
        'dem_date',
        (
            'dem_commune',
            lambda x: _db.session.query(RefGeoCommunes).get(x).nom_commune
        ),
        (
            'dem_designation',
            lambda x: _db.session.query(RefGeoBatiment).get(x).designation
        ),
        (
            'dmdr_service',
            lambda x: _db.session.query(Thesaurus).get(x).label if x else ''
        ),
        'dmdr_contact_nom',
        'dem_importance_travaux',
        (
            'dem_type_travaux',
            lambda x: _db.session.query(Thesaurus).get(x).label if x else ''
        ),
        'dem_description_travaux',
        (
            'plan_service',
            lambda x: _db.session.query(Thesaurus).get(x).label if x else ''
        ),
        'plan_entreprise',
        'plan_date',
        'plan_commentaire',
        'rea_date',
        'rea_duree',
        'rea_commentaire'
        ]


@routes.route('/', methods=['GET'])
@json_resp
@check_auth(groups=[
    'tizoutis-travaux-batiments-admin',
    'tizoutis-travaux-batiments-user'])
def get_all_trav_batiments():
    """
    retourne la liste des demandes de travaux sur batiments
    """
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
        print(annee)
        annee_deb = datetime.date(annee, 1, 1)
        annee_fin = datetime.date(annee, 12, 31)

        results = (
                _db.session.query(TravauxBatiment)
                .filter(
                    _db.and_(
                        TravauxBatiment.dem_date <= annee_fin,
                        _db.or_(
                            TravauxBatiment.rea_date == None,
                            TravauxBatiment.rea_date >= annee_deb
                        )
                    )
                )
                .all())
    except Exception:
        import traceback
        return [{'msg': traceback.format_exc()}], 400

    if _format == 'csv':
        return csv_response(TravauxBatimentFullSerializer.export_csv(results, fields=csv_fields), filename='travaux.csv')

    return [TravauxBatimentSerializer(res).serialize() for res in results]


@routes.route('/<id_trav>', methods=['GET'])
@json_resp
@check_auth(groups=[
    'tizoutis-travaux-batiments-admin',
    'tizoutis-travaux-batiments-user'])
def get_one_trav_batiment(id_trav):
    """
    Retourne le détail d'une fiche de demande de travaux
    """
    result = _db.session.query(TravauxBatiment).get(id_trav)
    return TravauxBatimentFullSerializer(result).serialize()


@routes.route('/', methods=['PUT', 'POST'])
@json_resp
@check_auth(groups=[
    'tizoutis-travaux-batiments-admin',
    'tizoutis-travaux-batiments-user'])
def create_trav_batiment():
    """
    Crée une nouvelle demande de travaux
    """
    dem = request.json
    dem['dem_date'] = datetime.datetime.now()

    demande = TravauxBatiment()
    try:
        TravauxBatimentFullSerializer(demande).populate(dem)
        _db.session.add(demande)
        _db.session.commit()


        send_mail(
                ['tizoutis-travaux-batiments-admin', 'admin-tizoutis'],
                "Création de la demande de travaux n°%s" % demande.id,
                '''
                Une nouvelle demande de travaux a été créée.
                Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/batiments?fiche=%s pour voir les détails de cette demande.
                ''' % demande.id,
                add_dests=demande.dmdr_contact_email.split(','),
                sendername='travaux-batiments'
                )
        return {'id': demande.id}
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<id_trav>', methods=['PUT', 'POST'])
@json_resp
@check_auth(groups=[
    'tizoutis-travaux-batiments-admin',
    'tizoutis-travaux-batiments-user'])
def update_trav_batiment(id_trav):
    """
    Met à jour une demande de travaux
    """
    dem = request.json

    trav = _db.session.query(TravauxBatiment).get(id_trav)
    try:
        TravauxBatimentFullSerializer(trav).populate(dem)
        _db.session.commit()

        send_mail(
                ['tizoutis-travaux-batiments-admin', 'admin-tizoutis'],
                "Mise à jour de la fiche n°%s" % trav.id,
                '''
                La fiche n°{0} a été modifiée.
                Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/batiments?fiche={0} pour voir les détails de cette demande.
                '''.format(trav.id),
                add_dests=trav.dmdr_contact_email.split(','),
                sendername='travaux-batiments'
                )

        return {'id': trav.id}
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<id_trav>', methods=['DELETE'])
@json_resp
@check_auth(groups=['tizoutis-travaux-batiments-admin'])
def delete_trav_batiment(id_trav):
    """
    Supprime une demande de travaux
    """
    trav = _db.session.query(TravauxBatiment).get(id_trav)
    _db.session.delete(trav)
    _db.session.commit()

    send_mail(
            ['tizoutis-travaux-batiments-admin', 'admin-tizoutis'],
            "Suppression de la fiche n°%s" % trav.id,
            '''
            La fiche n°{0} a été supprimée.
            Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/batiments pour voir la liste des travaux en cours.
            '''.format(trav.id),
            add_dests=trav.dmdr_contact_email.split(','),
            sendername='travaux-batiments'
            )
    return {'id': id_trav}

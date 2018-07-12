'''
Routes relatives aux demandes de travaux sur batiments
'''

import datetime

from flask import Blueprint, request, Response
from werkzeug.datastructures import Headers

from server import db as _db
from models import Fichier
from modules.thesaurus.models import Thesaurus
from modules.utils import (
        json_resp,
        send_mail,
        register_module
        )
from .models import (
        TravauxBatiment,
        TravauxBatimentSerializer,
        TravauxBatimentFullSerializer)
from serialize_utils import ValidationError

routes = Blueprint('travaux_batiments', __name__)

register_module('/travaux_batiments', routes)


@routes.route('/', methods=['GET'])
@json_resp
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
        annee_deb = datetime.date(annee, 1, 1)
        annee_fin = datetime.date(annee, 12, 31)

        results = (
                _db.session.query(TravauxBatiment)
                .filter(TravauxBatiment.dem_date.between(annee_deb, annee_fin))
                .all())
    except Exception:
        import traceback
        return [{'msg': traceback.format_exc()}], 400

    return [TravauxBatimentSerializer(res).serialize() for res in results]


@routes.route('/<id_trav>', methods=['GET'])
@json_resp
def get_one_trav_batiment(id_trav):
    """
    Retourne le détail d'une fiche de demande de travaux
    """
    result = _db.session.query(TravauxBatiment).get(id_trav)
    return TravauxBatimentFullSerializer(result).serialize()


@routes.route('/', methods=['PUT', 'POST'])
@json_resp
def create_trav_batiment():
    """
    Crée une nouvelle demande de travaux
    """
    dem = request.json
    dem['dem_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('dem_fichiers', [])]
    dem['plan_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('plan_fichiers', [])]
    dem['rea_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('rea_fichiers', [])]
    dem['dem_date'] = datetime.datetime.now()

    trav = TravauxBatiment()
    try:
        TravauxBatimentFullSerializer(trav).populate(dem)
        _db.session.add(trav)
        _db.session.commit()

        #TODO send mail
        send_mail(
                ['tizoutis-travaux-batiments-admin', 'admin-tizoutis'],
                "Création de la demande d'intervention n°%s" % trav.id,
                '''
                Une nouvelle demande d'intervention a été créée.
                Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/batiments?fiche=%s pour voir les détails de cette demande.
                ''' % trav.id,
                add_dests=trav.dmdr_contact_email.split(','),
                sendername='travaux-batiments'
                )

        return {'id': trav.id}
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<id_trav>', methods=['PUT', 'POST'])
@json_resp
def update_trav_batiment(id_trav):
    """
    Met à jour une demande de travaux
    """
    dem = request.json
    dem['dem_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('dem_fichiers', [])]
    dem['plan_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('plan_fichiers', [])]
    dem['rea_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('rea_fichiers', [])]

    trav = _db.session.query(TravauxBatiment).get(id_trav)
    try:
        TravauxBatimentFullSerializer(trav).populate(dem)
        _db.session.commit()

        #TODO send mail
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
def delete_trav_batiment(id_trav):
    """
    Supprime une demande de travaux
    """
    trav = _db.session.query(TravauxBatiment).get(id_trav)
    _db.session.delete(trav)
    _db.session.commit()

    #TODO send mail
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

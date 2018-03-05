'''
Routes relatives aux demandes d'intervention
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
        register_module,
        registered_funcs)
from .models import (
        Demande,
        DemandeSerializer,
        DemandeFullSerializer)
from serialize_utils import ValidationError


routes = Blueprint('interventions', __name__)

register_module('/interventions', routes)

check_auth = registered_funcs['check_auth']


def format_csv(data, sep='", "'):
    _fields = [
            'id', 'num_intv', 'dem_objet', 'dem_date', 'dem_localisation',
            'dem_details', 'dmdr_service', 'dem_delai', 'dem_loc_commune',
            'dem_loc_libelle', 'rea_duree', 'dmdr_contact_nom',
            'plan_commentaire', 'plan_date', 'rea_date', 'rea_nb_agents',
            'rea_commentaire']
    out = ['"%s"' % sep.join(_fields)]
    for item in data:
        line = DemandeFullSerializer(item).serialize(_fields)

        line['dem_localisation'] = (
                _db.session.query(Thesaurus)
                .get(line['dem_localisation'])
                .label)
        line['dem_objet'] = (
                _db.session.query(Thesaurus)
                .get(line['dem_objet'])
                .label)
        line['dmdr_service'] = (
                _db.session.query(Thesaurus)
                .get(line['dmdr_service'])
                .label)
        out.append('"%s"' % sep.join([
            str(col) if col else ''
            for col in line.values()]))
    headers = Headers()
    headers.add('Content-Type', 'text/plain')
    headers.add('Content-Disposition', 'attachment', filename='export.csv')
    return Response(('\n'.join(out)), headers=headers)


@routes.route('/', methods=['GET'])
@json_resp
def get_interventions():
    """
    retourne la liste des demandes d'intervention
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
                _db.session.query(Demande)
                .filter(Demande.dem_date.between(annee_deb, annee_fin))
                .all())
    except Exception:
        import traceback
        return [{'msg': traceback.format_exc()}], 400

    if _format == 'csv':
        return format_csv(results)
    if _format == 'tsv':
        return format_csv(results, "\t")

    else:
        return [DemandeSerializer(res).serialize() for res in results]


@routes.route('/<id_intervention>', methods=['GET'])
@json_resp
def get_one_intervention(id_intervention):
    """
    retourne une demande d'intervention identifiée par id_intervention
    """
    result = _db.session.query(Demande).get(id_intervention)
    return DemandeFullSerializer(result).serialize()


@routes.route('/', methods=['POST', 'PUT'])
@json_resp
def create_intervention():
    """
    crée une nouvelle demande d'intervention
    """
    dem = request.json
    dem['dem_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('dem_fichiers', [])]
    dem['rea_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('rea_fichiers', [])]
    dem['dem_date'] = datetime.datetime.now()

    demande = Demande()
    try:
        DemandeFullSerializer(demande).populate(dem)
        _db.session.add(demande)
        _db.session.commit()

        dem_loc = _db.session.query(Thesaurus).get(demande.dem_localisation).label
        dem_objet = _db.session.query(Thesaurus).get(demande.dem_objet).label
        send_mail(4, 6,
                "Création de la demande d'intervention n°%s - %s %s" % (
                    demande.id,
                    dem_objet,
                    dem_loc
                    ),
                '''
                Une nouvelle demande d'intervention a été créée.
                Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions?intervention=%s pour voir les détails de cette demande.
                ''' % demande.id,
                add_dests=demande.dmdr_contact_email.split(','),
                sendername='interventions'
                )

        return {'id': demande.id}
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<id_intervention>', methods=['POST', 'PUT'])
@json_resp
def update_intervention(id_intervention):
    """
    met à jour une demande d'intervention identifée par id_intervention
    """
    dem = request.json
    dem['dem_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('dem_fichiers', [])]
    dem['rea_fichiers'] = [
            _db.session.query(Fichier).get(item['id'])
            for item in dem.get('rea_fichiers', [])]

    demande = _db.session.query(Demande).get(id_intervention)
    try:
        DemandeFullSerializer(demande).populate(dem)
        _db.session.add(demande)
        _db.session.commit()

        dem_loc = _db.session.query(Thesaurus).get(demande.dem_localisation).label
        dem_objet = _db.session.query(Thesaurus).get(demande.dem_objet).label

        send_mail(4, 6,
                "Mise à jour de la demande d'intervention n°%s - %s %s" % (
                    demande.id,
                    dem_objet,
                    dem_loc
                    ),
                '''
                La demande d'intervention n°%s a été modifiée.
                Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions?intervention=%s pour voir les détails de cette demande.
                ''' % (demande.id, demande.id),
                add_dests=demande.dmdr_contact_email.split(','),
                sendername='interventions'
                )

        return {'id': demande.id}
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<id_intervention>', methods=['DELETE'])
@json_resp
def delete_intervention(id_intervention):
    """
    supprime une demande d'intervention identifiée par id_intervention
    """
    demande = _db.session.query(Demande).get(id_intervention)
    _db.session.delete(demande)
    _db.session.commit()

    dem_loc = _db.session.query(Thesaurus).get(demande.dem_localisation).label
    dem_objet = _db.session.query(Thesaurus).get(demande.dem_objet).label

    send_mail(4, 6,
            "Annulation de la demande d'intervention n°%s - %s %s" % (
                    demande.id,
                    dem_objet,
                    dem_loc
                    ),
            '''
            La demande d'intervention n°%s a été annulée.
            Vous pouvez vous connecter sur http://tizoutis.pnc.int/#/interventions/ pour voir la liste des demandes en cours.
            ''',
            add_dests=demande.dmdr_contact_email.split(','))

    return {'id': demande.id}

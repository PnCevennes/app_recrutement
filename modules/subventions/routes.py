import datetime

from flask import Blueprint, request, Response
from werkzeug.datastructures import Headers

from server import db as _db
from core.models import Fichier, prepare_fichiers, get_chrono, amend_chrono
from core.routes import upload_file, get_uploaded_file, delete_uploaded_file
from core.thesaurus.models import Thesaurus
from core.utils import (
        json_resp,
        csv_response,
        send_mail,
        register_module,
        registered_funcs
        )
from core.utils.serialize import ValidationError, load_ref
from .models import DemandeSubvention
from .serializers import SubvSerializer, SubvFullSerializer
from .utils import render


SubvFullSerializer.sub_fichiers.preparefn = prepare_fichiers(_db)
SubvFullSerializer.dec_fichiers.preparefn = prepare_fichiers(_db)
SubvFullSerializer.pai_fichiers.preparefn = prepare_fichiers(_db)


routes = Blueprint('subventions', __name__)

register_module('/subventions', routes)

check_auth = registered_funcs['check_auth']



csv_fields = [
        'meta_createur',
        'meta_createur_mail',
        'meta_id',
        'meta_statut',
        'meta_observations',
        'pet_nom',
        'pet_civ',
        'pet_adresse',
        'pet_cpostal',
        'pet_commune',
        'pet_telephone',
        'pet_mobile',
        'pet_mail',
        ('sa_massif', load_ref(_db, Thesaurus, 'label')),
        ('sa_service', load_ref(_db, Thesaurus, 'label')),
        'sa_instructeur',
        'sa_tel_instr',
        'sa_mail_instr',
        ('sa_commission', load_ref(_db, Thesaurus, 'label')),
        ('sa_axe_charte', load_ref(_db, Thesaurus, 'label')),
        'sa_id_action',
        'sa_nature',
        'sub_objet',
        'sub_commune',
        'sub_zc',
        'sub_ctr_patri',
        'sub_montant',
        'sub_cout_total',
        'sub_taux',
        ('sub_date_rcpt', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        'sub_dem_pc',
        ('sub_date_ar', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('dec_date_bureau', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        'dec_num_delib',
        'dec_motif_refus',
        'dec_conditions',
        'dec_montant',
        'dec_tva',
        'dec_taux',
        ('dec_compte', load_ref(_db, Thesaurus, 'label')),
        ('dec_code_ug', load_ref(_db, Thesaurus, 'label')),
        ('dec_operation', load_ref(_db, Thesaurus, 'label')),
        'dec_num_ej',
        ('dec_date_notif', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('dec_date_retour', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('dec_echeance', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('dec_prorogation', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('pai_date_recept_demande', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        'pai_accpt1_montant',
        'pai_accpt1_date',
        'pai_accpt1_dp',
        'pai_accpt2_montant',
        'pai_accpt2_date',
        'pai_accpt2_dp',
        'pai_accpt3_montant',
        'pai_accpt3_date',
        'pai_accpt3_dp',
        'pai_accpt4_montant',
        'pai_accpt4_date',
        'pai_accpt4_dp',
        'pai_accpt5_montant',
        'pai_accpt5_date',
        'pai_accpt5_dp',
        'pai_total_verse',
        'pai_reste_du',
        'pai_mnt_annule',
        ]


@routes.route('/')
@json_resp
def get_subs():
    print('subs')
    _format = request.args.get('format', 'dict')
    subs = _db.session.query(DemandeSubvention).all()
    if _format == 'csv':
        return csv_response(SubvFullSerializer.export_csv(subs, fields=csv_fields), filename='subventions.csv')
    return [SubvSerializer(sub).serialize() for sub in subs]


@routes.route('/<int:id_sub>', methods=['GET'])
@json_resp
def get_detail_subv(id_sub):
    _format = request.args.get('format', 'dict')
    _template = request.args.get('template', None)
    subv = _db.session.query(DemandeSubvention).get(id_sub)
    if _format == 'document':
        _data = SubvFullSerializer(subv).dump(csv_fields)
        if _template:
            return render(_template, 'subv.rtf', _data)
        else:
            return _data

    return SubvFullSerializer(subv).serialize()


@routes.route('/', methods=['POST', 'PUT'])
@json_resp
def create_subv():
    dem = request.json
    ref_chrono = '{}S'.format(dem['sub_date_rcpt'][2:4])
    demande = DemandeSubvention()
    try:
        dem['meta_id'] = get_chrono(ref_chrono)
        SubvFullSerializer(demande).populate(dem)
        _db.session.add(demande)
        _db.session.commit()
        return {'id': demande.id, 'meta_id': demande.meta_id}
    except ValidationError as e:
        amend_chrono(ref_chrono)
        return e.errors, 400


@routes.route('/<int:id_sub>', methods=['POST', 'PUT'])
@json_resp
def update_subv(id_sub):
    dem = request.json
    demande = _db.session.query(DemandeSubvention).get(id_sub)
    if not demande:
        return {}, 404
    try:
        SubvFullSerializer(demande).populate(dem)
        _db.session.commit()
        return SubvFullSerializer(demande).serialize()
    except ValidationError as e:
        return e.errors, 400


@routes.route('/<int:id_sub>', methods=['DELETE'])
@json_resp
def delete_subv(id_sub):
    demande = _db.session.query(DemandeSubvention).get(id_sub)
    if not demande:
        return {}, 404
    _db.session.delete(demande)
    _db.session.commit()
    return {'id': demande.id}

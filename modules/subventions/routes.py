import datetime
import os, os.path

from flask import Blueprint, request, Response, current_app
from werkzeug.datastructures import Headers
from werkzeug.utils import secure_filename

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
from core.utils.serialize import ValidationError, load_ref, format_phone
from .models import DemandeSubvention, SubvTemplate
from .serializers import (
        SubvSerializer,
        SubvFullSerializer,
        SubvTemplateSerializer
        )
from .utils import render, montant2txt


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
        'pet_adresse2',
        'pet_cpostal',
        'pet_commune',
        ('pet_telephone', format_phone),
        ('pet_mobile', format_phone),
        'pet_mail',
        ('sa_massif', load_ref(_db, Thesaurus, 'label')),
        ('sa_service', load_ref(_db, Thesaurus, 'label')),
        'sa_instructeur',
        ('sa_tel_instr', format_phone),
        'sa_mail_instr',
        ('sa_commission', load_ref(_db, Thesaurus, 'label')),
        ('sa_axe_charte', load_ref(_db, Thesaurus, 'label')),
        'sa_id_action',
        'sa_nature',
        'sub_objet',
        'sub_commune',
        'sub_zc',
        'sub_ctr_patri',
        ('sub_montant', lambda x: ('%.2f' % x).replace('.', ',')),
        ('sub_cout_total', lambda x: ('%.2f' % x).replace('.', ',')),
        ('sub_taux', lambda x: ('%.2f' % x).replace('.', ',')),
        ('sub_date_rcpt', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        'sub_dem_pc',
        ('sub_date_ar', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('dec_date_bureau', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        'dec_num_delib',
        'dec_motif_refus',
        'dec_conditions',
        ('dec_montant', lambda x: ('%.2f' % x).replace('.', ',')),
        ('dec_tva', lambda x: 'HT' if x == 1 else 'TTC'),
        ('dec_taux', lambda x: ('%.2f' % x).replace('.', ',')),
        ('dec_compte', load_ref(_db, Thesaurus, 'label')),
        ('dec_code_ug', load_ref(_db, Thesaurus, 'label')),
        ('dec_operation', load_ref(_db, Thesaurus, 'label')),
        'dec_num_ej',
        ('dec_date_notif', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('dec_date_retour', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('dec_echeance', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('dec_prorogation', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('pai_date_recept_demande', lambda x: '/'.join(list(reversed(x.split('-')))) if x else ''),
        ('pai_accpt1_montant', lambda x: ('%.2f' % x).replace('.', ',')),
        'pai_accpt1_date',
        'pai_accpt1_dp',
        ('pai_accpt2_montant', lambda x: ('%.2f' % x).replace('.', ',')),
        'pai_accpt2_date',
        'pai_accpt2_dp',
        ('pai_accpt3_montant', lambda x: ('%.2f' % x).replace('.', ',')),
        'pai_accpt3_date',
        'pai_accpt3_dp',
        ('pai_accpt4_montant', lambda x: ('%.2f' % x).replace('.', ',')),
        'pai_accpt4_date',
        'pai_accpt4_dp',
        ('pai_accpt5_montant', lambda x: ('%.2f' % x).replace('.', ',')),
        'pai_accpt5_date',
        'pai_accpt5_dp',
        ('pai_total_verse', lambda x: ('%.2f' % x).replace('.', ',')),
        ('pai_reste_du', lambda x: ('%.2f' % x).replace('.', ',')),
        ('pai_mnt_annule', lambda x: ('%.2f' % x).replace('.', ',')),
        ]


#
# Routes gestion des subventions
#

@routes.route('/')
@json_resp
def get_subs():
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
            _data['sub_montant_txt'] = montant2txt(_data['sub_montant'], sep=',').upper()
            _data['dec_montant_txt'] = montant2txt(_data['dec_montant'], sep=',').upper()
            return render(_template, _data)
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


#
# Routes gestion des modèles
#

@routes.route('/templates', methods=['GET'])
@json_resp
def get_templates():
    tpls = _db.session.query(SubvTemplate).all()
    return [SubvTemplateSerializer(tpl).dump() for tpl in tpls]



@routes.route('/templates', methods=['POST'])
@json_resp
def add_template():
    if not 'id' in request.form:
        tpl = SubvTemplate()
        if not 'fichier' in request.files:
            return {'err': 'No File'}, 400
    else:
        tpl = _db.session.query(SubvTemplate).get(request.form['id'])

    ser = SubvTemplateSerializer(tpl)
    ser.load(request.form)

    if 'fichier' in request.files:
        fichier = request.files['fichier']
        fname = secure_filename(fichier.filename)
        path = os.path.join(current_app.config['TEMPLATES_DIR'], 'subventions', fname)
        fichier.save(path)
        ser.path = path
    if not tpl.id:
        _db.session.add(tpl)
        _db.session.flush()
    _db.session.commit()
    return ser.dump()

@routes.route('/templates/<id_template>', methods=['DELETE'])
@json_resp
def remove_template(id_template):
    tpl = _db.session.query(SubvTemplate).get(id_template)
    if not tpl:
        return {}, 404
    _db.session.delete(tpl)
    _db.session.commit()
    same_path = _db.session.query(SubvTemplate).filter(SubvTemplate.path == tpl.path).all()
    if not len(same_path):
        os.unlink(tpl.path)
    return {'deleted_id': tpl.id}

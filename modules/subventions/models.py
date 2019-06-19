'''
mapping subventions
'''

from server import db
from core.models import Fichier, serialize_files
from core.thesaurus.models import Thesaurus


class DemandeSubvention(db.Model):
    __tablename__ = 'subv_demande'
    id = db.Column(db.Integer, primary_key=True)
    # Fiche
    meta_createur = db.Column(db.Unicode(150))
    meta_createur_mail = db.Column(db.Unicode(150))
    meta_id = db.Column(db.Unicode(20))
    meta_statut = db.Column(db.Integer)
    meta_observations = db.Column(db.UnicodeText)
    # Petitionnaire
    pet_nom = db.Column(db.Unicode(150))
    pet_civ = db.Column(db.Unicode(20))
    pet_adresse = db.Column(db.Unicode(255))
    pet_adresse2 = db.Column(db.Unicode(255))
    pet_cpostal = db.Column(db.Unicode(10))
    pet_commune = db.Column(db.Unicode(50))
    pet_telephone = db.Column(db.Unicode(20))
    pet_mobile = db.Column(db.Unicode(20))
    pet_mail = db.Column(db.Unicode(150))
    # Suivi administratif
    sa_massif = db.Column(db.Integer)
    sa_service = db.Column(db.Integer)
    sa_instructeur = db.Column(db.Unicode(150))
    sa_tel_instr = db.Column(db.Unicode(20))
    sa_mail_instr = db.Column(db.Unicode(150))
    sa_commission = db.Column(db.Integer)
    sa_axe_charte = db.Column(db.Integer)
    sa_id_action = db.Column(db.Unicode(10))
    sa_nature = db.Column(db.Unicode(150))
    # Subvention
    sub_objet = db.Column(db.UnicodeText)
    sub_commune = db.Column(db.UnicodeText)
    sub_zc = db.Column(db.Integer)
    sub_ctr_patri = db.Column(db.Integer)
    sub_montant = db.Column(db.Numeric(10, 2))
    sub_cout_total = db.Column(db.Numeric(10, 2))
    sub_taux = db.Column(db.Numeric(10, 2))
    sub_date_rcpt = db.Column(db.Date)
    sub_dem_pc = db.Column(db.Date)
    sub_date_ar = db.Column(db.Date)
    # Décision
    dec_date_bureau = db.Column(db.Date)
    dec_num_delib = db.Column(db.Unicode(20))
    dec_motif_refus = db.Column(db.UnicodeText)
    dec_conditions = db.Column(db.UnicodeText)
    dec_montant = db.Column(db.Numeric(10, 2))
    dec_tva = db.Column(db.Integer)
    dec_taux = db.Column(db.Numeric(10, 2))
    dec_compte = db.Column(db.Integer)
    dec_code_ug = db.Column(db.Integer)
    dec_operation = db.Column(db.Integer)
    dec_num_ej = db.Column(db.Unicode(20))
    dec_date_notif = db.Column(db.Date)
    dec_date_retour = db.Column(db.Date)
    dec_relance = db.Column(db.Date)
    dec_echeance = db.Column(db.Date)
    dec_prorogation = db.Column(db.Date)
    # Paiement
    pai_date_recept_demande = db.Column(db.Date)
    pai_accpt1_montant = db.Column(db.Numeric(10, 2))
    pai_accpt1_date = db.Column(db.Date)
    pai_accpt1_dp = db.Column(db.Unicode(30))
    pai_accpt2_montant = db.Column(db.Numeric(10, 2))
    pai_accpt2_date = db.Column(db.Date)
    pai_accpt2_dp = db.Column(db.Unicode(30))
    pai_accpt3_montant = db.Column(db.Numeric(10, 2))
    pai_accpt3_date = db.Column(db.Date)
    pai_accpt3_dp = db.Column(db.Unicode(30))
    pai_accpt4_montant = db.Column(db.Numeric(10, 2))
    pai_accpt4_date = db.Column(db.Date)
    pai_accpt4_dp = db.Column(db.Unicode(30))
    pai_accpt5_montant = db.Column(db.Numeric(10, 2))
    pai_accpt5_date = db.Column(db.Date)
    pai_accpt5_dp = db.Column(db.Unicode(30))
    pai_total_verse = db.Column(db.Numeric(10, 2))
    pai_reste_du = db.Column(db.Integer)
    pai_mnt_annule = db.Column(db.Numeric(10, 2))

    sub_fichiers = db.relationship(
            Fichier,
            secondary='subv_rel_sub_fichier',
            lazy='joined'
            )

    dec_fichiers = db.relationship(
            Fichier,
            secondary='subv_rel_dec_fichier',
            lazy='joined'
            )

    pai_fichiers = db.relationship(
            Fichier,
            secondary='subv_rel_pai_fichier',
            lazy='joined'
            )


class RelSubFichier(db.Model):
    __tablename__ = 'subv_rel_sub_fichier'
    id_dem_sub = db.Column(
            db.Integer,
            db.ForeignKey('subv_demande.id'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id),
            primary_key=True)


class RelDecFichier(db.Model):
    __tablename__ = 'subv_rel_dec_fichier'
    id_dem_sub = db.Column(
            db.Integer,
            db.ForeignKey('subv_demande.id'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id),
            primary_key=True)


class RelPaiFichier(db.Model):
    __tablename__ = 'subv_rel_pai_fichier'
    id_dem_sub = db.Column(
            db.Integer,
            db.ForeignKey('subv_demande.id'),
            primary_key=True)
    id_fichier = db.Column(
            db.Integer,
            db.ForeignKey(Fichier.id),
            primary_key=True)


class SubvTemplate(db.Model):
    __tablename__ = 'subv_template'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50))
    label = db.Column(db.Unicode(50))
    public = db.Column(db.Integer)
    path = db.Column(db.Unicode(255))

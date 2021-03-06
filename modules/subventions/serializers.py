import datetime
from core.utils.serialize import (
    Serializer,
    Field,
    IntField,
    FloatField,
    DateField,
    FileField
)


class SubvSerializer(Serializer):
    '''
    Serialize une partie des données pour un affichage
    résumé en liste
    '''
    id = Field()
    meta_id = Field()
    pet_nom = Field()
    sa_massif = IntField()
    sa_commission = IntField()
    dec_date_bureau = DateField()
    dec_echeance = DateField()
    pai_reste_du = FloatField()
    meta_statut = IntField()


class SubvFullSerializer(SubvSerializer):
    meta_createur = Field()
    meta_createur_mail = Field()
    meta_observations = Field()
    # Petitionnaire
    pet_civ = Field()
    pet_adresse = Field()
    pet_adresse2 = Field()
    pet_cpostal = Field()
    pet_commune = Field()
    pet_telephone = Field()
    pet_mobile = Field()
    pet_mail = Field()
    # Suivi administratif
    sa_service = IntField()
    sa_instructeur = Field()
    sa_tel_instr = Field()
    sa_mail_instr = Field()
    sa_axe_charte = IntField()
    sa_id_action = Field()
    sa_nature = Field()
    sa_date_commission = DateField()
    # Subvention
    sub_objet = Field()
    sub_commune = Field()
    sub_zc = IntField(default=0)
    sub_ctr_patri = IntField()
    sub_montant = FloatField(default=0)
    sub_cout_total = FloatField(default=0)
    sub_taux = FloatField(default=0)
    sub_date_rcpt = DateField()
    sub_dem_pc = DateField()
    sub_date_ar = DateField()
    # Décision
    dec_date_notif = DateField()
    dec_num_delib = Field()
    dec_refus_ajourn = IntField()
    dec_motif_refus = Field()
    dec_conditions = Field()
    dec_montant = FloatField(default=0)
    dec_tva = IntField(default=0)
    dec_taux = FloatField(default=0)
    dec_compte = IntField()
    dec_code_ug = IntField()
    dec_operation = IntField()
    dec_num_ej = Field()
    dec_date_retour = DateField()
    dec_relance = DateField()
    dec_dem_prorogation_date = DateField()
    dec_bur_prorogation_date = DateField()
    dec_numdel_prorogation = Field()
    dec_prorogation = DateField()
    dec_motif_ajourn = Field()
    dec_bur_ajourn_date = DateField()
    dec_numdel_ajourn = Field()
    dec_courrier_ajourn = DateField()
    # Paiement
    pai_date_recept_demande = DateField()
    pai_accpt1_montant = FloatField()
    pai_accpt1_date = DateField()
    pai_accpt1_dp = Field()
    pai_accpt2_montant = FloatField()
    pai_accpt2_date = DateField()
    pai_accpt2_dp = Field()
    pai_accpt3_montant = FloatField()
    pai_accpt3_date = DateField()
    pai_accpt3_dp = Field()
    pai_accpt4_montant = FloatField()
    pai_accpt4_date = DateField()
    pai_accpt4_dp = Field()
    pai_accpt5_montant = FloatField()
    pai_accpt5_date = DateField()
    pai_accpt5_dp = Field()
    pai_total_verse = FloatField()
    pai_mnt_annule = FloatField()

    sub_fichiers = FileField()
    dec_fichiers = FileField()
    pai_fichiers = FileField()


class SubvTemplateSerializer(Serializer):
    id = IntField()
    name = Field()
    label = Field()
    public = Field(
        preparefn=lambda x: 1 if x == 'true' else 0,
        serializefn=lambda x: x == 1
    )
    path = Field()

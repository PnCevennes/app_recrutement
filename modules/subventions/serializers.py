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
    dec_echeance = DateField()
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
    dec_date_bureau = DateField()
    dec_num_delib = Field()
    dec_motif_refus = Field()
    dec_conditions = Field()
    dec_montant = FloatField(default=0)
    dec_tva = IntField(default=0)
    dec_taux = FloatField(default=0)
    dec_compte = IntField()
    dec_code_ug = IntField()
    dec_operation = IntField()
    dec_num_ej = Field()
    dec_date_notif = DateField()
    dec_date_retour = DateField()
    dec_prorogation = DateField()
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
    pai_reste_du = FloatField()
    pai_mnt_annule = FloatField()

    sub_fichiers = FileField()
    dec_fichiers = FileField()
    pai_fichiers = FileField()

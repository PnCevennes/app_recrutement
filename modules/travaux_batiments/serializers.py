from core.utils.serialize import (
    Serializer,
    Field,
    IntField,
    DateField,
    FileField)


class TravauxBatimentSerializer(Serializer):
    '''
    serialise une partie des données de la fiche pour
    un affichage en liste
    '''
    id = IntField()
    dem_date = DateField()
    dem_commune = Field()
    dem_designation = Field()
    rea_date = DateField()


class TravauxBatimentFullSerializer(TravauxBatimentSerializer):
    '''
    serialise la totalité de la fiche pour un affichage détaillé
    '''
    dmdr_service = IntField()
    dmdr_contact_nom = Field()
    dmdr_contact_email = Field(
            serializefn=(
                lambda val: [item for item in val.split(',') if item]),
            preparefn=lambda val: ','.join(val)
            )
    dem_importance_travaux = Field()
    dem_type_travaux = Field()
    dem_description_travaux = Field()
    plan_service = IntField()
    plan_entreprise = Field()
    plan_date = Field()
    plan_commentaire = Field()
    rea_date = DateField()
    rea_duree = IntField(default=0)
    rea_commentaire = Field()
    dem_fichiers = FileField()
    plan_fichiers = FileField()
    rea_fichiers = FileField()




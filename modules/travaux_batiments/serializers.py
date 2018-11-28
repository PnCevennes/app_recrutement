from modules.utils.serialize import (
    Serializer,
    Field,
    prepare_date,
    prepare_serial,
    serialize_date)
from models import serialize_files


class TravauxBatimentSerializer(Serializer):
    '''
    serialise une partie des données de la fiche pour
    un affichage en liste
    '''
    id = Field(preparefn=prepare_serial)
    dem_date = Field(
            serializefn=serialize_date,
            preparefn=prepare_date)
    dem_commune = Field()
    dem_designation = Field()
    rea_date = Field(
            serializefn=serialize_date,
            preparefn=prepare_date)


class TravauxBatimentFullSerializer(TravauxBatimentSerializer):
    '''
    serialise la totalité de la fiche pour un affichage détaillé
    '''
    dmdr_service = Field()
    dmdr_contact_nom = Field()
    dmdr_contact_email = Field(
            serializefn=(
                lambda val: [item for item in val.split(',') if item]),
            preparefn=lambda val: ','.join(val)
            )
    dem_importance_travaux = Field()
    dem_type_travaux = Field()
    dem_description_travaux = Field()
    plan_service = Field()
    plan_entreprise = Field()
    plan_date = Field(
            serializefn=serialize_date,
            preparefn=prepare_date)
    plan_commentaire = Field()
    rea_date = Field(
            serializefn=serialize_date,
            preparefn=prepare_date)
    rea_duree = Field()
    rea_commentaire = Field()
    dem_fichiers = Field(serializefn=serialize_files)
    plan_fichiers = Field(serializefn=serialize_files)
    rea_fichiers = Field(serializefn=serialize_files)




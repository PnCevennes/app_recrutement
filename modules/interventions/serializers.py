from modules.utils.serialize import Serializer, Field, prepare_date
from models import serialize_files


class DemandeSerializer(Serializer):
    id = Field()
    num_intv = Field()
    dem_date = Field(serializefn=str, preparefn=prepare_date)
    dem_objet = Field()
    dem_loc_libelle = Field()
    rea_date = Field(
            serializefn=(lambda val: str(val) if val is not None else val),
            preparefn=prepare_date)


class DemandeFullSerializer(DemandeSerializer):
    dem_localisation = Field()
    dem_loc_commune = Field()
    dem_details = Field()
    dem_delai = Field()
    dem_fichiers = Field(serializefn=serialize_files)

    dmdr_contact_nom = Field()
    dmdr_service = Field()
    dmdr_contact_email = Field(
            serializefn=(
                lambda val: [item for item in val.split(',') if item]),
            preparefn=lambda val: ','.join(val)
            )

    plan_date = Field()
    plan_commentaire = Field()

    rea_duree = Field()
    rea_nb_agents = Field()
    rea_commentaire = Field()
    rea_fichiers = Field(serializefn=serialize_files)


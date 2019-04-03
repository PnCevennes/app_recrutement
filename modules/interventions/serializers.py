from core.utils.serialize import (
        Serializer,
        Field,
        IntField,
        DateField,
        FileField)


class DemandeSerializer(Serializer):
    id = IntField()
    num_intv = Field()
    dem_date = DateField()
    dem_objet = Field()
    dem_loc_libelle = Field()
    rea_date = DateField()


class DemandeFullSerializer(DemandeSerializer):
    dem_localisation = IntField()
    dem_loc_commune = Field()
    dem_details = Field()
    dem_delai = Field()
    dem_fichiers = FileField()

    dmdr_contact_nom = Field()
    dmdr_service = IntField()
    dmdr_contact_email = Field(
            serializefn=(
                lambda val: [item for item in val.split(',') if item]),
            preparefn=lambda val: ','.join(val)
            )

    plan_date = Field()
    plan_commentaire = Field()

    rea_duree = IntField(default=0)
    rea_nb_agents = IntField(default=0)
    rea_commentaire = Field()
    rea_fichiers = FileField()


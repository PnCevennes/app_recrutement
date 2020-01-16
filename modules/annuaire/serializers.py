'''
Classes de sérialisation des données
'''
from core.utils.serialize import Serializer, Field, IntField, DateField, format_phone

from .models import Entite


def prepare_relations(data):
    return Entite.query.filter(
        Entite.id.in_(
            [item['id'] for item in data if item]
        )
    ).all()


def serialize_relations(data):
    return [
        {'id':item.id, 'label': item.label}
        for item in data if item
    ]


class EntiteSerializer(Serializer):
    id = IntField()
    meta_update_date = DateField()
    meta_update_user = Field()
    nom = Field()
    label = Field(readonly=True)
    type_entite = Field()
    observations = Field()
    parents = Field(
        preparefn=prepare_relations,
        serializefn=serialize_relations,
        default=[]
    )
    relations = Field(
        preparefn=prepare_relations,
        serializefn=serialize_relations,
        default=[]
    )


class CommuneSerializer(EntiteSerializer):
    adresse = Field()
    adresse2 = Field()
    code_postal = Field()
    telephone = Field(serializefn=format_phone)
    email = Field()
    site_internet = Field()


class CorrespondantSerializer(EntiteSerializer):
    civilite = Field()
    prenom = Field()
    fonction = Field()
    adresse = Field()
    adresse2 = Field()
    code_postal = Field()
    telephone = Field(serializefn=format_phone)
    mobile = Field(serializefn=format_phone)
    email = Field()


class EntrepriseSerializer(EntiteSerializer):
    nom_gerant = Field()
    prenom_gerant = Field()
    adresse = Field()
    adresse2 = Field()
    code_postal = Field()
    telephone = Field(serializefn=format_phone)
    telephone2 = Field(serializefn=format_phone)
    email = Field()
    alt_email = Field()
    site_internet = Field()

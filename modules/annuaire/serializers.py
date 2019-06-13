'''
Classes de sérialisation des données
'''
from core.utils.serialize import Serializer, Field, IntField, format_phone


class EntiteSerializer(Serializer):
    id = IntField()
    nom = Field()
    label = Field(readonly=True)
    type_entite = Field()
    observations = Field()
    parents = Field(
            preparefn=lambda data: [item['id'] for item in data if item],
            default=[]
            )
    relations = Field(
            preparefn=lambda data: [item['id'] for item in data if item],
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

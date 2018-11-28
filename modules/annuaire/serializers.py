'''
Classes de sérialisation des données
'''
from modules.utils.serialize import Serializer, Field


def format_phone(tel):
    '''
    formate un numéro de téléphone
    '''
    try:
        tel = (tel.replace(' ', '')
                .replace('.', '')
                .replace('/', '')
                .replace('-', ''))
        return ' '.join(a+b for a, b in zip(
                    [x for x in tel[::2]],
                    [y for y in tel[1::2]]))
    except:
        return tel


class EntiteSerializer(Serializer):
    id = Field()
    nom = Field()
    label = Field(readonly=True)
    type_entite = Field()
    observations = Field()
    parents = Field(
            preparefn=lambda data: [item['id'] for item in data if item]
            )
    relations = Field(
            preparefn=lambda data: [item['id'] for item in data if item]
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


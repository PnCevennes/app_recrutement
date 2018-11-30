from core.utils.serialize import (
    Serializer,
    Field,
    prepare_date,
    serialize_date)
from core.models import serialize_files


class AgentSerializer(Serializer):
    '''
    serialise une partie des données de la fiche pour
    un affichage en liste
    '''
    id = Field()
    nom = Field()
    prenom = Field()
    intitule_poste = Field()
    service_id = Field()
    arrivee = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )
    depart = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )


class AgentDetailSerializer(AgentSerializer):
    '''
    serialise la totalité de la fiche pour un affichage détaillé
    '''
    id_agent = Field()
    desc_mission = Field()
    notif_list = Field(
            serializefn=(
                lambda val: [item for item in val.split(',') if item]),
            preparefn=lambda val: ','.join(val)
            )
    type_contrat = Field()
    lieu = Field()
    logement = Field()  # TH ref 10
    categorie = Field()  # TH ref 38
    referent = Field()
    gratification = Field()
    temps_travail = Field()  # TH ref 33
    temps_travail_autre = Field()
    residence_administrative = Field()
    convention_signee = Field()
    bureau = Field()
    observations = Field()
    meta_create = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )
    meta_update = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )
    meta_createur_fiche = Field()
    materiel = Field(
            serializefn=lambda val: [item.id for item in val]
            )
    fichiers = Field(serializefn=serialize_files)

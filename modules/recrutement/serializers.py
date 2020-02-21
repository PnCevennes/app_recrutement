import datetime
from core.utils.serialize import (
    Serializer,
    Field,
    IntField,
    DateField,
    FileField,
    MultipleField
)


class AgentSerializer(Serializer):
    '''
    serialise une partie des données de la fiche pour
    un affichage en liste
    '''
    id = IntField()
    nom = Field()
    prenom = Field()
    intitule_poste = Field()
    service_id = IntField()
    arrivee = DateField()
    depart = DateField()


class AgentDetailSerializer(AgentSerializer):
    '''
    serialise la totalité de la fiche pour un affichage détaillé
    '''
    id_agent = IntField()
    desc_mission = Field()
    notif_list = Field(
        serializefn=(
            lambda val: [item for item in val.split(',') if item]),
        preparefn=lambda val: ','.join(val)
    )
    type_contrat = IntField()
    lieu = IntField()
    logement = IntField()  # TH ref 10
    categorie = IntField()  # TH ref 38
    referent = Field()
    gratification = Field()
    temps_travail = IntField()  # TH ref 33
    temps_travail_autre = Field()
    residence_administrative = Field()
    convention_signee = Field()
    bureau = Field()
    observations = Field()
    meta_create = DateField(default=str(datetime.date.today()))
    meta_update = DateField(default=None)
    meta_createur_fiche = Field()
    materiel = MultipleField(
        serializefn=lambda val: [item.id for item in val]
    )
    fichiers = FileField()

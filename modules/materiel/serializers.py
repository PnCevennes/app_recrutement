import datetime
from core.utils.serialize import (
    Serializer,
    Field,
    IntField,
    DateField,
    FileField
)
from .models import Affectation


class TypeMaterielSerializer(Serializer):
    id = IntField()
    label = Field()
    observations = Field()


class AffectationSerializer(Serializer):
    id = IntField()
    id_materiel = IntField()
    type_affectation = IntField()
    utilisateur = Field()
    date_affectation = DateField(default=datetime.datetime.now())
    date_retour = DateField()
    observations = Field()


class MaterielSerializer(Serializer):
    id = IntField()
    type_mat = IntField(preparefn=lambda x: x['id'])
    label = Field()
    reference = Field()
    disponible = IntField()
    utilisateur_actuel = Field()


class MaterielFullSerializer(MaterielSerializer):
    observations = Field()
    date_entree = DateField(default=datetime.datetime.now())
    date_exclusion = DateField()
    etat = Field()
    '''
    affectations = Field(
        preparefn=lambda x: [AffectationSerializer(Affectation).load(o) for o in x],
        serializefn=lambda x: [AffectationSerializer(o).dump() for o in x] if x else []
    )
    '''

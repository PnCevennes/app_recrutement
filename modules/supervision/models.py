'''
mapping supervision
'''
import datetime
import json

from server import db
from core.utils.serialize import (
    Serializer,
    Field,
    IntField,
    DateField
)


class EvtEquipementSerializer(Serializer):
    id = IntField()
    equip_id = IntField()
    evt_type = IntField()
    evt_date = DateField()


class EquipementSerializer(Serializer):
    '''
    Serialisation d'un objet Equipement
    '''
    id = IntField()
    ip_addr = Field()
    label = Field()
    equip_type = Field()
    status = Field()
    stats = Field(
        serializefn=lambda x: json.loads(x) if x else [],
        preparefn=json.dumps
    )
    last_up = DateField()
    commentaires = Field()
    evts = Field(
        serializefn=lambda x: [
            EvtEquipementSerializer(evt).serialize()
            for evt in reversed(x)
        ] if x else []
    )


class EvtEquipement(db.Model):
    '''
    Mapping d'un événement sur un équipement
    '''
    __tablename__ = 'sup_evt_equipement'
    id = db.Column(db.Integer, primary_key=True)
    equip_id = db.Column(
        db.Integer,
        db.ForeignKey('sup_equipement.id')
    )
    evt_type = db.Column(db.Integer)
    evt_date = db.Column(db.DateTime)


class Equipement(db.Model):
    '''
    Mapping d'un équipement réseau
    '''
    __tablename__ = 'sup_equipement'
    id = db.Column(db.Integer, primary_key=True)
    ip_addr = db.Column(db.Unicode(length=20))
    label = db.Column(db.Unicode(length=50))
    equip_type = db.Column(db.Integer)
    status = db.Column(db.Integer)
    stats = db.Column(db.UnicodeText)
    last_up = db.Column(db.DateTime)
    commentaires = db.Column(db.UnicodeText)
    evts = db.relationship(EvtEquipement, lazy='joined', cascade='delete')

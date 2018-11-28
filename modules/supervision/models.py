'''
mapping supervision
'''
import datetime
import json

from server import db
from modules.utils.serialize import (
    Serializer,
    Field,
    prepare_date,
    serialize_date)


class EquipementSerializer(Serializer):
    '''
    Serialisation d'un objet Equipement
    '''
    id = Field()
    ip_addr = Field()
    label = Field()
    equip_type = Field()
    status = Field()
    stats = Field(
            serializefn=lambda x: json.loads(x) if x else [],
            preparefn=json.dumps
            )
    last_up = Field(
            serializefn=serialize_date,
            preparefn=prepare_date
            )
    commentaires = Field()


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


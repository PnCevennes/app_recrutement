'''
mapping thésaurus
'''
from server import db
from core.utils.serialize import Serializer, Field, IntField


class ThesaurusSerializer(Serializer):
    id = Field()
    id_ref = Field()
    label = Field()
    menu = IntField(serializefn=lambda x: bool(x))


class Thesaurus(db.Model):
    __tablename__ = 'th_thesaurus'
    id = db.Column(db.Integer, primary_key=True)
    id_ref = db.Column(db.Integer)
    label = db.Column(db.Unicode(length=50))
    menu = db.Column(db.Integer)

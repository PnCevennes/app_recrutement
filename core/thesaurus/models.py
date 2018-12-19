'''
mapping thésaurus
'''
from server import db
from core.utils.serialize import Serializer, Field


class ThesaurusSerializer(Serializer):
    id = Field()
    id_ref = Field()
    label = Field()


class Thesaurus(db.Model):
    __tablename__ = 'th_thesaurus'
    id = db.Column(db.Integer, primary_key=True)
    id_ref = db.Column(db.Integer)
    label = db.Column(db.Unicode(length=50))

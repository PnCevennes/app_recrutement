from server import db
from serialize_utils import serializer, Serializer, Field, ValidationError


@serializer
class FichierSerializer(Serializer):
    id = Field()
    filename = Field()
    file_uri = Field()


class Fichier(db.Model):
    __tablename__ = 'commons_fichier'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Unicode(length=255))

    @property
    def file_uri(self):
        return '%s_%s' % (self.id, self.filename)

    def to_json(self):
        return {
                'id': self.id,
                'filename': self.filename,
                'file_uri': self.file_uri
                }

def serialize_files(data):
    return [FichierSerializer(item).serialize() for item in data]

from server import db
from modules.utils.serialize import Serializer, Field



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
    if not data:
        return []
    return [FichierSerializer(item).serialize() for item in data]


def prepare_fichiers(db):
    '''
    retourne une liste de fichiers
    '''
    def _prepare_fichiers(val):
        return [db.session.query(Fichier).get(item['id'])
                    for item in val]
    return _prepare_fichiers



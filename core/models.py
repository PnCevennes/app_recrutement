from server import db
from core.utils.serialize import Serializer, Field, serialize_files


class Chrono(db.Model):
    __tablename__ = 'commons_chrono'
    reference = db.Column(db.Unicode(length=50), primary_key=True)
    cur_id = db.Column(db.Integer)


def get_chrono(reference):
    '''
    Retourne un numéro de chrono relatif à la référence fournie
    '''
    current = db.session.query(Chrono).get(reference)
    if not current:
        current = Chrono(reference=reference, cur_id=1)
        db.session.add(current)
    else:
        current.cur_id += 1
    db.session.commit()
    return '{}{:03}'.format(current.reference, current.cur_id)


def amend_chrono(reference):
    '''
    Annule la précédente demande de chrono relatif à la référence fournie
    '''
    current = db.session.query(Chrono).get(reference)
    if current:
        current.cur_id -= 1
        db.session.commit()
        return True
    return False


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


def prepare_fichiers(db):
    '''
    retourne une liste de fichiers
    '''
    def _prepare_fichiers(val):
        return [db.session.query(Fichier).get(item['id'])
                    for item in val]
    return _prepare_fichiers



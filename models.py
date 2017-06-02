from server import db


class Fichier(db.Model):
    __tablename__ = 'commons_fichier'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Unicode(length=255))

    def get_file_uri(self):
        return '%s_%s' % (self.id, self.filename)

    def to_json(self):
        return {
                'id': self.id,
                'filename': self.filename,
                'file_uri': self.get_file_uri()
                }

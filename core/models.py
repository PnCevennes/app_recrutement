import datetime
import json
from enum import Enum

from flask import g

from server import db
from core.utils.serialize import (
    Serializer,
    Field,
    IntField,
    DateField,
    serialize_files # noqa
    )


class ChangeType(Enum):
    CREATE = 1
    UPDATE = 2
    DELETE = 3


class Changelog(db.Model):
    __tablename__ = 'commons_changelog'
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.Unicode(length=50))
    model_name = db.Column(db.Unicode(length=50))
    entity_id = db.Column(db.Integer)
    author = db.Column(db.Unicode(length=100))
    change_type = db.Column(db.Integer)
    change_date = db.Column(db.Date)
    changes = db.Column(db.UnicodeText)


class ChangelogSerializer(Serializer):
    id = IntField()
    entity_id = IntField()
    author = Field()
    change_type = IntField()
    change_date = DateField()


def record_changes(model, changes, change_type, pkname='id'):
    logger = Changelog()
    logger.model_name = model.__class__.__name__
    logger.module_name = model.__class__.__module__
    logger.entity_id = getattr(model, pkname)
    logger.author = g.userdata['name']
    logger.change_type = change_type.value
    logger.change_date = datetime.datetime.today()
    logger.changes = json.dumps(changes)
    db.session.add(logger)
    db.session.commit()


def map_changes(log):
    log.changes = json.loads(log.changes)
    log.change_type = ChangeType(log.change_type)
    return log


def load_changes(instance, full=False):
    results = db.session.query(Changelog).filter(
        db.and_(
            Changelog.module_name == instance.__class__.__module__,
            Changelog.model_name == instance.__class__.__name__,
            Changelog.entity_id == instance.id
        )
    ).all()
    if full:
        return [map_changes(x) for x in results]
    else:
        return [ChangelogSerializer(x).dump() for x in results]


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

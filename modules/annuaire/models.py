'''
mapping agent
'''
from collections import OrderedDict

from sqlalchemy.ext.hybrid import hybrid_property

from server import db


class RelationEntite(db.Model):
    __tablename__ = 'ann_relations'
    id_parent = db.Column(
        db.Integer,
        db.ForeignKey('ann_entite.id'),
        primary_key=True
    )
    id_enfant = db.Column(
        db.Integer,
        db.ForeignKey('ann_entite.id'),
        primary_key=True
    )


class Entite(db.Model):
    __tablename__ = 'ann_entite'
    __mapper_args__ = {
        'polymorphic_identity': 'entite',
        'polymorphic_on': 'type_entite'
    }
    id = db.Column(db.Integer, primary_key=True)
    meta_update_date = db.Column(db.Date)
    meta_update_user = db.Column(db.Unicode(length=100))
    _nom = db.Column(db.Unicode(length=255))
    _label = db.Column('nom_complet', db.Unicode(length=255))
    type_entite = db.Column(db.Unicode(50))
    observations = db.Column(db.Unicode(length=1000))
    relations = db.relationship(
        'Entite',
        secondary='ann_relations',
        primaryjoin=id == RelationEntite.id_parent,
        secondaryjoin=id == RelationEntite.id_enfant,
        join_depth=0,
        backref='parents'
    )


    @hybrid_property
    def label(self):
        return self._label

    @hybrid_property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, val):
        self._nom = val
        self._label = val


class Commune(Entite):
    __tablename__ = 'ann_commune'
    __mapper_args__ = {
        'polymorphic_identity': 'commune',
    }
    id_entite = db.Column(
        db.Integer,
        db.ForeignKey('ann_entite.id'),
        primary_key=True)
    adresse = db.Column(db.Unicode(length=255))
    adresse2 = db.Column(db.Unicode(length=255))
    code_postal = db.Column(db.Unicode(length=50))
    telephone = db.Column(db.Unicode(length=20))
    email = db.Column(db.Unicode(length=255))
    site_internet = db.Column(db.Unicode(length=255))


class Correspondant(Entite):
    __tablename__ = 'ann_correspondant'
    __mapper_args__ = {
        'polymorphic_identity': 'correspondant',
    }
    id_entite = db.Column(
        db.Integer,
        db.ForeignKey('ann_entite.id'),
        primary_key=True)
    civilite = db.Column(db.Unicode(length=50))
    _prenom = db.Column('prenom', db.Unicode(length=100))
    adresse = db.Column(db.Unicode(length=255))
    adresse2 = db.Column(db.Unicode(length=255))
    code_postal = db.Column(db.Unicode(length=50))
    telephone = db.Column(db.Unicode(length=20))
    mobile = db.Column(db.Unicode(length=20))
    email = db.Column(db.Unicode(length=255))
    fonction = db.Column(db.Unicode(length=100))

    @hybrid_property
    def label(self):
        return self._label

    @hybrid_property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, val):
        self._nom = val
        self._label = '%s %s' % (val, self._prenom)

    @hybrid_property
    def prenom(self):
        return self._prenom

    @prenom.setter
    def prenom(self, val):
        self._prenom = val
        self._label = '%s %s' % (self.nom, val)


class Entreprise(Entite):
    __tablename__ = 'ann_entreprise'
    __mapper_args__ = {
        'polymorphic_identity': 'entreprise',
    }
    id_entite = db.Column(
        db.Integer,
        db.ForeignKey('ann_entite.id'),
        primary_key=True)
    nom_gerant = db.Column(db.Unicode(length=100))
    prenom_gerant = db.Column(db.Unicode(length=100))
    fonction_gerant = db.Column(db.Unicode(length=255))
    adresse = db.Column(db.Unicode(length=255))
    adresse2 = db.Column(db.Unicode(length=255))
    code_postal = db.Column(db.Unicode(length=50))
    telephone = db.Column(db.Unicode(length=20))
    telephone2 = db.Column(db.Unicode(length=20))
    email = db.Column(db.Unicode(length=255))
    alt_email = db.Column(db.Unicode(length=255))
    site_internet = db.Column(db.Unicode(length=255))

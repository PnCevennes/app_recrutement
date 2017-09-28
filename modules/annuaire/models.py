#coding: utf8

'''
mapping agent
'''

from server import db 
from sqlalchemy.ext.hybrid import hybrid_property
from collections import OrderedDict


class ValidationError(Exception):
    def __init__(self, errors):
        self.error_list = errors



class Validateur(object):
    def validate(self, data):
        print('validate')
        out = {}
        unhandled = {}
        errors = []
        for key in data:
            if key in self.fields:
                if not self.fields[key](data[key]):
                    raise errors.append(key)
                out[key] = data[key]
            else:
                unhandled[key] = data[key]
        if errors:
            raise ValidationError(errors)
        return out, unhandled


class EntiteValidateur(Validateur):
        fields = OrderedDict((
                ('id', lambda x: True),
                ('nom', lambda x: True),
                ('type_entite', lambda x: True),
                ('observations', lambda x: True)
                ))



class Entite(db.Model):
    __tablename__ = 'ann_entite'
    __mapper_args__ = {
            'polymorphic_identity': 'entite',
            'polymorphic_on': 'type_entite'
            }
    id = db.Column(db.Integer, primary_key=True)
    _nom = db.Column(db.Unicode(length=255))
    _label = db.Column('nom_complet', db.Unicode(length=255))
    type_entite = db.Column(db.Integer)
    observations = db.Column(db.Unicode(length=1000))

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


    @property
    def relations(self):
        rels = RelationEntite.query.filter(RelationEntite.id_parent==self.id).all()
        relations = Entite.query.filter(Entite.id.in_([r.id_enfant for r in rels])).order_by(Entite.label).all()
        return [{'id':rel.id, 'label': rel.label} for rel in relations]


    @relations.setter
    def relations(self, values):
        rels = RelationEntite.query.filter(RelationEntite.id_parent==self.id).all()
        for r in rels:
            db.session.delete(r)
        for v in values:
            n = RelationEntite(id_parent=self.id, id_enfant=v)
            db.session.add(n)


    @property
    def parents(self):
        rels = RelationEntite.query.filter(RelationEntite.id_enfant==self.id).all()
        parents = Entite.query.filter(Entite.id.in_([r.id_parent for r in rels])).all()
        return [{'id':rel.id, 'label': rel.label} for rel in parents]


    @parents.setter
    def parents(self, values):
        rels = RelationEntite.query.filter(RelationEntite.id_enfant==self.id).all()
        for r in rels:
            db.session.delete(r)
        for v in values:
            n = RelationEntite(id_parent=v, id_enfant=self.id)
            db.session.add(n)

    def delete_relations(self):
        rels = RelationEntite.query.filter(RelationEntite.id_parent==self.id).all()
        parents = RelationEntite.query.filter(RelationEntite.id_enfant==self.id).all()
        for r in rels:
            db.session.delete(r)
        for p in parents:
            db.session.delete(p)



    def to_json(self):
        fields = ['id', 'nom', 'observations', 'type_entite',
                'relations', 'label', 'parents']
        out = {field: getattr(self, field, '') for field in fields}
        return out


class CommuneValidateur(Validateur):
    fields = OrderedDict((
                ('id', lambda x: True),
                ('nom', lambda x: True),
                ('adresse', lambda x: True),
                ('adresse2', lambda x: True),
                ('code_postal', lambda x: True),
                ('telephone', lambda x: True),
                ('email', lambda x: True),
                ('site_internet', lambda x: True),
                ('type_entite', lambda x: True),
                ('observations', lambda x: True)
                ))



class Commune(Entite):
    __tablename__ = 'ann_commune'
    __mapper_args__ = {
            'polymorphic_identity': 'commune',
            }
    id_entite = db.Column(db.Integer, db.ForeignKey('ann_entite.id'), primary_key=True)
    adresse = db.Column(db.Unicode(length=255))
    adresse2 = db.Column(db.Unicode(length=255))
    code_postal = db.Column(db.Unicode(length=50))
    telephone = db.Column(db.Unicode(length=20))
    email = db.Column(db.Unicode(length=255))
    site_internet = db.Column(db.Unicode(length=255))

    def to_json(self):
        fields = ['id', 'nom', 'observations', 'adresse', 'adresse2', 
                'code_postal', 'telephone', 'email', 'site_internet', 
                'type_entite', 'relations', 'parents', 'label']
        return {field: getattr(self, field, '') for field in fields}



class CorrespondantValidateur(Validateur):
    fields = OrderedDict((
                ('id', lambda x: True),
                ('civilite', lambda x: True),
                ('nom', lambda x: True),
                ('prenom', lambda x: True),
                ('fonction', lambda x: True),
                ('adresse', lambda x: True),
                ('code_postal', lambda x: True),
                ('telephone', lambda x: True),
                ('mobile', lambda x: True),
                ('email', lambda x: True),
                ('type_entite', lambda x: True),
                ('observations', lambda x: True)
                ))


class Correspondant(Entite):
    __tablename__ = 'ann_correspondant'
    __mapper_args__ = {
            'polymorphic_identity': 'correspondant',
            }
    id_entite = db.Column(db.Integer, db.ForeignKey('ann_entite.id'), primary_key=True)
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

    def to_json(self):
        fields = ['id', 'nom', 'observations', 'prenom', 'fonction',
                'adresse', 'adresse2', 'code_postal', 'telephone', 'mobile',
                'email', 'type_entite', 'relations', 'parents', 'label',
                'civilite']
        return {field: getattr(self, field, '') for field in fields}



class EntrepriseValidateur(Validateur):
    fields = OrderedDict((
        ('id', lambda x: True),
        ('nom', lambda x: True),
        ('nom_gerant', lambda x: True),
        ('prenom_gerant', lambda x: True),
        ('fonction_gerant', lambda x: True),
        ('adresse', lambda x: True),
        ('adresse2', lambda x: True),
        ('code_postal', lambda x: True),
        ('telephone', lambda x: True),
        ('telephone2', lambda x: True),
        ('email', lambda x: True),
        ('alt_email', lambda x: True),
        ('site_internet', lambda x: True),
        ('observations', lambda x: True)
        ))



class Entreprise(Entite):
    __tablename__ = 'ann_entreprise'
    __mapper_args__ = {
            'polymorphic_identity': 'entreprise',
            }
    id_entite = db.Column(db.Integer, db.ForeignKey('ann_entite.id'), primary_key=True)
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

    def to_json(self):
        fields = ['id',
                'nom',
                'observations',
                'nom_gerant',
                'prenom_gerant',
                'fonction_gerant',
                'adresse',
                'adresse2',
                'code_postal',
                'telephone',
                'telephone2',
                'email',
                'alt_email',
                'site_internet',
                'relations',
                'parents',
                'label',
                'type_entite']
        return {field: getattr(self, field, '') for field in fields}




class RelationEntite(db.Model):
    __tablename__ = 'ann_relations'
    id_parent = db.Column(
            db.Integer,
            db.ForeignKey('ann_entite.id'),
            primary_key=True)
    id_enfant = db.Column(
            db.Integer,
            db.ForeignKey('ann_entite.id'),
            primary_key=True)

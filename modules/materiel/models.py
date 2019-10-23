'''
mappings matériel
'''

from server import db

class Affectation(db.Model):
    '''
    Affectation ou emprunt
    '''
    __tablename__ = 'invent_affectation'
    id = db.Column(db.Integer, primary_key=True)
    id_materiel = db.Column(db.Integer, db.ForeignKey('invent_materiel.id'))
    # materiel = db.relationship(Materiel, backref="affectations")
    type_affectation = db.Column(db.Integer)
    utilisateur = db.Column(db.Unicode(50))
    date_affectation = db.Column(db.Date)
    date_retour = db.Column(db.Date)
    observations = db.Column(db.UnicodeText)


class TypeMateriel(db.Model):
    '''
    Thésaurus dynamique des différents types de matériel
    '''
    __tablename__ = 'invent_type_mat'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.Unicode(length=100))
    observations = db.Column(db.UnicodeText)


class Materiel(db.Model):
    '''
    Matériel avec numéro d'inventaire
    '''
    __tablename__ = 'invent_materiel'
    id = db.Column(db.Integer, primary_key=True)
    type_mat = db.Column(db.Integer)
    label = db.Column(db.Unicode(length=100))
    reference = db.Column(db.Unicode(length=50))
    observations = db.Column(db.UnicodeText)
    date_entree = db.Column(db.Date)
    date_exclusion = db.Column(db.Date)
    etat = db.Column(db.Integer)
    disponible = db.Column(db.Integer)
    utilisateur_actuel = db.Column(db.Unicode(length=50))
    affectations = db.relationship(Affectation, backref="materiel")

'''
mapping ref geo
'''
from server import db


class RefGeoCommunes(db.Model):
    """
    Communes sur lesquelles le parc entretien des bâtiments
    """
    __tablename__ = 'ref_geo_commune'
    id = db.Column(db.Integer, primary_key=True)
    nom_commune = db.Column(db.Unicode(255))


class RefGeoBatiment(db.Model):
    """
    Bâtiments entretenus par le parc
    """
    __tablename__ = 'ref_geo_batiment'
    id = db.Column(db.Integer, primary_key=True)
    ref_commune = db.Column(db.Integer)
    reference = db.Column(db.Unicode(10))
    lieu_dit = db.Column(db.Unicode(255))
    designation = db.Column(db.Unicode(255))

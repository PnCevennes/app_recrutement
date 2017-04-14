#coding: utf8

from modules.annuaire.models import Entite, Commune, Correspondant, RelationEntite, db

db.create_all()

g1 = Entite(nom='groupe1')
g2 = Entite(nom='groupe2')

c1 = Commune(nom='commune1', site_internet='www.example.com')
c2 = Commune(nom='commune2', site_internet='www.foo.com')

p1 = Correspondant(nom='personne1', prenom='prenom1', email='personne1@example.com')
p2 = Correspondant(nom='personne2', prenom='prenom2', email='personne2@foo.com')


db.session.add_all([g1, g2, c1, c2, p1, p2])
db.session.flush()

r1 = RelationEntite(id_parent=g1.id, id_enfant=c1.id)
r2 = RelationEntite(id_parent=g1.id, id_enfant=p1.id)

db.session.add_all([r1, r2])

db.session.commit()


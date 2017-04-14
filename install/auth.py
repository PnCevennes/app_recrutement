#coding: utf8

from modules.auth.models import User, Application, AppUser, db

db.create_all()
apps = [
    Application(nom='Administration'),
    Application(nom='Annuaire'),
    Application(nom='Recrutement')]

user = User(login='admin', password='admin', email='admin@example.com')

rels = [
    AppUser(niveau=6, user=user, application=apps[0]),
    AppUser(niveau=6, user=user, application=apps[1]),
    AppUser(niveau=6, user=user, application=apps[2])]

db.session.add_all(apps)
db.session.add(user)
db.session.add_all(rels)
db.session.commit()

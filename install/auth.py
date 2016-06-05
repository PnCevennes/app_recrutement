#coding: utf8

from server import db
from modules.auth.models import User, Application, AppUser

db.create_all()

app = Application(nom='Recrutement')

user = User(login='admin', password='admin', email='admin@example.com')

rel = AppUser(niveau=6, user=user, application=app)

db.session.add(app)
db.session.add(user)
db.session.add(rel)
db.session.commit()

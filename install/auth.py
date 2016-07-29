#coding: utf8

from server import db
from modules.auth.models import User, Application, AppUser

db.create_all()

app = Application(nom='Administration')
app1 = Application(nom='Annuaire')
app2 = Application(nom='Recrutement')

user = User(login='admin',
        password='admin',
        email='admin@example.com'
        )

rel1 = AppUser(niveau=6, user=user, application=app)
rel2 = AppUser(niveau=6, user=user, application=app1)
rel3 = AppUser(niveau=6, user=user, application=app2)

db.session.add_all([app, app1, app2, rel1, rel2, rel3])
db.session.add(user)
db.session.commit()

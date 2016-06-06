#coding: utf8

from server import db
from modules.recrutement.models import AgentDetail
from modules.thesaurus.models import Thesaurus
import datetime

db.create_all()

#récupération elems thesaurus
lieu = db.session.query(Thesaurus).filter(Thesaurus.label=='Florac').one()
serv = db.session.query(Thesaurus).filter(Thesaurus.label=='SG').one()
loge = db.session.query(Thesaurus).filter(Thesaurus.label=='Grézo').one()
cont = db.session.query(Thesaurus).filter(Thesaurus.label=='Stage').one()



#Création agent test
ag = AgentDetail(
    nom='Hochon', 
    prenom='Paul', 
    service_id=serv.id,
    lieu=lieu.id,
    type_contrat=cont.id,
    logement=loge.id,
    arrivee=datetime.date(2016, 7, 1),
    depart=datetime.date(2016, 8, 31)
    )

db.session.add(ag)
db.session.commit()

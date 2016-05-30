#coding: utf8
'''
Module d'initialisation de l'application
Crée les éléments de test
'''

from server import db
from modules.agents.models import AgentDetail
from modules.thesaurus.models import Thesaurus
import datetime


#crée la base de données
db.create_all()

#création des références thésaurus
t1 = Thesaurus(id_ref=0, label="lieux d'affectation")
t2 = Thesaurus(id_ref=0, label='services')
t3 = Thesaurus(id_ref=0, label='logements')
t4 = Thesaurus(id_ref=0, label='types contrat')

db.session.add_all([t1, t2, t3, t4])
db.session.commit()

#Création lieux
lieux = [
    Thesaurus(id_ref=t1.id, label='Florac'),
    Thesaurus(id_ref=t1.id, label='Genolhac'),
    Thesaurus(id_ref=t1.id, label='Pont de Monvert'),
    Thesaurus(id_ref=t1.id, label='Crozes'),
    Thesaurus(id_ref=t1.id, label='Ales'),
    Thesaurus(id_ref=t1.id, label='Villaret'),
    Thesaurus(id_ref=t1.id, label='Vigan'),
    Thesaurus(id_ref=t1.id, label='Serreyrede')
    ]

db.session.add_all(lieux)

#Création services
services = [
    Thesaurus(id_ref=t2.id, label='Direction'),
    Thesaurus(id_ref=t2.id, label='SAS'),
    Thesaurus(id_ref=t2.id, label='SCVT'),
    Thesaurus(id_ref=t2.id, label='SDD'),
    Thesaurus(id_ref=t2.id, label='SG')
    ]

db.session.add_all(services)

#Création logements
logements = [
    Thesaurus(id_ref=t3.id, label='Logement perso'),
    Thesaurus(id_ref=t3.id, label='Logement fonction'),
    Thesaurus(id_ref=t3.id, label='Grézo'),
    Thesaurus(id_ref=t3.id, label='Autre')
    ]

db.session.add_all(logements)

#Création types de contrat
contrats = [
    Thesaurus(id_ref=t4.id, label='CDI'),
    Thesaurus(id_ref=t4.id, label='CDD'),
    Thesaurus(id_ref=t4.id, label='Saisonnier'),
    Thesaurus(id_ref=t4.id, label='Stage')
    ]

db.session.add_all(contrats)
db.session.commit()

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
    arrivee=datetime.date(2016, 6, 1),
    depart=datetime.date(2016, 8, 31)
    )

db.session.add(ag)
db.session.commit()

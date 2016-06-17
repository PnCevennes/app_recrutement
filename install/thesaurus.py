#coding: utf8

from server import db
from modules.thesaurus.models import Thesaurus

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
    Thesaurus(id_ref=t4.id, label='Permanent'),
    Thesaurus(id_ref=t4.id, label='CDD'),
    Thesaurus(id_ref=t4.id, label='Saisonnier'),
    Thesaurus(id_ref=t4.id, label='Stage')
    ]

db.session.add_all(contrats)

materiel = [
    Thesaurus(id_ref=0, label='Matériel'),
    Thesaurus(id_ref=26, label='Véhicule de service'),
    Thesaurus(id_ref=26, label='Ordinateur fixe'),
    Thesaurus(id_ref=26, label='Ordinateur portable'),
    Thesaurus(id_ref=26, label='Téléphone fixe'),
    Thesaurus(id_ref=26, label='Téléphone portable'),
    ]

db.session.add_all(materiel)

temps_travail = [
    Thesaurus(id_ref=0, label='Temps de travail'),
    Thesaurus(id_ref=32, label='100%'),
    Thesaurus(id_ref=32, label='90%'),
    Thesaurus(id_ref=32, label='80%'),
    Thesaurus(id_ref=32, label='50%'),
    Thesaurus(id_ref=32, label='Autre')
    ]

db.session.add_all(temps_travail)

categories = [
    Thesaurus(id_ref=0, label='Catégorie'),
    Thesaurus(id_ref=38, label='A'),
    Thesaurus(id_ref=38, label='B'),
    Thesaurus(id_ref=38, label='C'),
    ]

db.session.add_all(categories)


db.session.commit()


from core.thesaurus.models import Thesaurus
from server import db

'''
DEJA EXECUTE

compte_charge = Thesaurus(id_ref=0, label='compte_charge_subs')
db.session.add(compte_charge)
db.session.flush()
db.session.commit()

th_compte = ('65731', '65732', '65733', '65734')

for t in th:
    item = Thesaurus(id_ref=compte_charge.id, label=t)
    db.session.add(item)

db.session.commit()

ope_sub = Thesaurus(id_ref=0, label='operation_sub')
db.session.add(ope_sub)
db.session.flush()
db.session.commit()


commission = Thesaurus(id_ref=0, label='commission')
axe_charte = Thesaurus(id_ref=0, label='axe_charte')
service_desc = Thesaurus(id_ref=0, label='service_desc')
db.session.add(commission)
db.session.add(axe_charte)
db.session.add(service_desc)
db.session.flush()
db.session.commit()
'''

ope_sub = Thesaurus.query.filter(Thesaurus.label == 'operation_sub').one()
commission = Thesaurus.query.filter(Thesaurus.label == 'commission').one()
axe_charte = Thesaurus.query.filter(Thesaurus.label == 'axe_charte').one()
service_desc = Thesaurus.query.filter(Thesaurus.label == 'services_desc').one()

th_ope = (
    'VALOPAT',
    'ACCESNAT',
    'CONGCVT',
    'CONCULTURE',
    'AGRIENV',
    'ARCHITECT',
    'CHASSE',
    'SYLVDURABLE',
    'URBANISME',
    'GENIEMILIEUX'
)

th_com = (
    'Agriculture',
    'Architecture, Urbanisme et Paysage',
    'Biodiversité',
    'Cynégétique',
    'EEDD Sensibilisation',
    'Forêt',
    'Patrimoine Culturel',
    'Tourisme'
)

th_charte = (
    'Axe 1 : Faire vivre notre culture',
    'Axe 2 : Protéger la nature, le patrimoine et les paysages',
    "Axe 3 : Gérer et préserver l'eau et les milieux aquatiques",
    'Axe 4 : Vivre et habiter',
    "Axe 5 : Favoriser l'agriculture",
    'Axe 6 : Valoriser la forêt',
    'Axe 7 : Dynamiser le tourisme',
    'Axe 8 : Soutenir une chasse gestionnaire'
)

th_servdesc = (
    'Service Direction',
    'Service Accueil et Sensibilisation',
    'Service Connaissance et Veille du Territoire',
    'Service Développement Durable',
    'Secrétariat Général'
)

for r, th in (
    (ope_sub, th_ope),
    (commission, th_com),
    (axe_charte, th_charte),
    (service_desc, th_servdesc)
):
    for t in th:
        item = Thesaurus(id_ref=r.id, label=t)
        db.session.add(item)

db.session.commit()

import datetime


'''
Fonctions utilitaires de l'annuaire
'''


vcard_tpl = '''BEGIN:VCARD
VERSION:2.1
N:%s;%s
FN:%s
TITLE:%s
TEL;WORK;VOICE:%s%s
EMAIL;PREF;INTERNET:%s
REV:%s
END:VCARD'''


def format_vcard(entite):
    '''
    retourne une vcard formatee selon les donnees de l'entite fournie
    '''
    dtime = datetime.datetime.now()
    return vcard_tpl % (
        entite.nom,
        entite.prenom,
        entite.label,
        entite.fonction,
        entite.telephone,
        (
            "\nTEL;CELL;VOICE:%s" % entite.mobile
            if entite.mobile else ''
        ),
        entite.email,
        dtime.strftime('%Y%m%dT%H%m%SZ')
    )

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
        entite.nom or '',
        entite.prenom or '',
        entite.label or '',
        entite.fonction or '',
        format_phone(entite.telephone),
        (
            "\nTEL;CELL;VOICE:%s" % format_phone(entite.mobile)
            if entite.mobile else ''
        ),
        entite.email or '',
        dtime.strftime('%Y%m%dT%H%m%SZ')
        )


def format_csv(corresps, fields, sep=','):
    '''
    retourne une liste de correspondants sous format tabulaire CSV
    '''
    if not len(corresps):
        return ''

    correspondants = [corresp.to_json() for corresp in corresps]
    outdata = [sep.join(fields)]
    for item in correspondants:
        outdata.append(
                sep.join(['"%s"' % str(item.get(e) or '').replace('"', '""') for e in fields]))
    out = '\r\n'.join(outdata)
    return out.encode('latin1', 'replace')



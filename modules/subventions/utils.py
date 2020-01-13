import os.path
import rtfunicode

from flask import Response, current_app
from werkzeug.datastructures import Headers

from server import db
from .models import SubvTemplate


def render(templatename, data):
    '''
    Crée un document RTF à partir du modèle dont le nom est fourni
    et retourne un objet Response
    '''
    tpl = db.session.query(SubvTemplate).filter(
        SubvTemplate.name == templatename
    ).one()
    with open(tpl.path, 'r') as fp:
        template = fp.read().encode('ascii')
        for varname, value in data.items():
            varmod = b'#' + varname.encode('ascii') + b'#'
            value = (str(value).encode('rtfunicode')
                     if value and len(str(value)) else b'')
            template = template.replace(varmod, value, -1)

    headers = Headers()
    headers.add('Content-Type', 'text/rtf')
    headers.add(
        'Content-Disposition',
        'attachment',
        filename='%s.rtf' % templatename
    )
    headers.add('Cache-Control', 'no-cache')
    return Response(template, headers=headers)


def chunk2txt(chunk):
    '''
    Retourne un groupe de trois chiffres maximum sur forme de texte
    '''
    _tr_base = [
        '',
        'un',
        'deux',
        'trois',
        'quatre',
        'cinq',
        'six',
        'sept',
        'huit',
        'neuf'
    ]
    _tr_dix = [
        '',
        'dix',
        'vingt',
        'trente',
        'quarante',
        'cinquante',
        'soixante',
        'soixante-dix',
        'quatre-vingt',
        'quatre-vingt-dix'
    ]
    _reps = {
        'dix-un': 'onze',
        'dix-deux': 'douze',
        'dix-trois': 'treize',
        'dix-quatre': 'quatorze',
        'dix-cinq': 'quinze',
        'dix-six': 'seize',
        'vingt-un': 'vingt-et-un',
        'trente-un': 'trente-et-un',
        'quarante-un': 'quarante-et-un',
        'cinquante-un': 'cinquante-et-un',
        'soixante-un': 'soixante-et-un',
        'soixante-onze': 'soixante-et-onze'
    }
    out = []
    for idx, num in enumerate(chunk):
        if idx == 2:
            if int(num) > 1:
                out.extend(['cent', _tr_base[int(num)]])
            elif int(num):
                out.append('cent')
        elif idx == 1:
            out.append(_tr_dix[int(num)])
        else:
            out.append(_tr_base[int(num)])
    tmpstr = '-'.join(list(filter(len, reversed(out))))

    # application particularités
    for _old, _new in _reps.items():
        tmpstr = tmpstr.replace(_old, _new)
    if tmpstr.endswith('cent') and tmpstr != 'cent':
        tmpstr = tmpstr + 's'
    if tmpstr.endswith('quatre-vingt'):
        tmpstr = tmpstr + 's'
    return tmpstr


def nb2txt(nb):
    '''
    Retourne la valeur fournie sous forme de texte
    '''
    _mils = ['', 'mille', 'million', 'milliard']
    nb = ''.join(list(reversed(str(nb))))
    chunks = [nb[x:x + 3] for x in range(0, len(nb), 3)]
    out = []
    for idx, chunk in enumerate(chunks):
        if chunk != '000':
            out.append(_mils[idx])
        out.append(chunk2txt(chunk))
    final = ('-'.join(list(reversed(out)))).strip()
    final = final.replace('un-mille', 'mille')
    final = final.replace('mille-un', 'mille-et-un')
    if 'million' in final and not final.startswith('un-million'):
        final = final.replace('million', 'millions')
    if 'milliard' in final and not final.startswith('un-milliard'):
        final = final.replace('milliard', 'milliards')
    if final.endswith('-'):
        final = final[:-1]
    return final


def montant2txt(nb, sep='.'):
    '''
    Retourne un montant sous forme de texte
    '''
    try:
        euros, cents = str(nb).split(sep)
        eurs = nb2txt(euros)
        cts = nb2txt(cents)
        if len(cts.strip()):
            return '%s euros et %s centimes' % (eurs, cts)
        else:
            return '%s euros' % eurs
    except ValueError:
        return '%s euros' % nb2txt(nb)

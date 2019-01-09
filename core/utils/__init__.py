'''
Fonctions utilitaires
'''

import json
import threading

from functools import wraps
from flask import Response
from flask_mail import Message
from werkzeug.datastructures import Headers

from server import get_app, db, mail

registered_modules = {}
registered_funcs = {}


def csv_response(data, filename='export.csv'):
    '''
    Retourne les entêtes HTTP pour les fichiers CSV
    '''
    headers = Headers()
    headers.add('Content-Type', 'text/csv')
    headers.add('Content-Disposition', 'attachment', filename=filename)
    return Response(data, headers=headers)


def vcard_response(data, filename='export.vcf'):
    '''
    Retourne les entêtes HTTP pour les fichiers VCARD
    '''
    headers = Headers()
    headers.add('Content-Type', 'text/plain')
    headers.add('Content-Disposition', 'attachment', filename='export.vcf')
    return Response(data, headers=headers)


def register_module(prefix, blueprint):
    '''
    Importe les routes d'un module dans l'application
    '''
    registered_modules[prefix] = blueprint


def json_resp(fn):
    '''
    Décorateur transformant le résultat renvoyé par une vue
    en objet JSON
    '''
    @wraps(fn)
    def _json_resp(*args, **kwargs):
        res = fn(*args, **kwargs)
        if isinstance(res, tuple):
            res, status = res
        else:
            status = 200
        if isinstance(res, Response):
            return res
        return Response(
                json.dumps(res),
                status=status,
                mimetype='application/json')
    return _json_resp


def _send_async(app, msg, groups):
    from core.auth.utils import ldap_connect, get_user_groups
    with app.app_context():
        ldap_cnx = ldap_connect(
                app.config['LDAP_USER'],
                app.config['LDAP_PASS'])
        ldap_cnx.search(
                'ou=Personnel,dc=pnc,dc=int',
                '(sn=*)',
                attributes=['cn', 'mail', 'memberOf'])
        for entry in ldap_cnx.entries:
            user_groups = get_user_groups(entry)
            for grp in groups:
                if grp in user_groups:
                    msg.add_recipient(str(entry.mail))
                    break

        mail.send(msg)


def send_mail(
        groups, subject, msg_body,
        add_dests=None, sendername='recrutement'):
    '''
    envoie un mail aux administrateurs de l'application
    '''
    if add_dests is None:
        add_dests = []

    # supprimer chaines vides dans listes email
    add_dests = list(filter(lambda x: len(x), add_dests))

    app = get_app()
    if not app.config['SEND_MAIL']:
        return

    dests = add_dests

    msg = Message(
            '[%s] %s' % (sendername, subject),
            sender=app.config['MAIL_SENDER'],
            recipients=dests)
    msg.body = msg_body

    thr = threading.Thread(target=_send_async, args=[app, msg, groups])
    thr.start()


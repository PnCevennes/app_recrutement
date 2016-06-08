#coding: utf8
'''
Fonctions utilitaires
'''

from server import db, mail, get_app
from functools import wraps
from flask import Response
from flask.ext.mail import Message
import json


registered_modules = {}
registered_funcs = {}

def register_module(prefix, blueprint):
    '''
    Importe les routes d'un module dans l'application
    '''
    registered_modules[prefix] = blueprint


def _normalize(obj, columns):
    '''
    Retourne un dictionnaire dont les clés sont le tableau de colonnes
    fourni (`columns`) et les valeurs sont issues de l'objet `obj` fourni.
    '''
    out = {}
    for col in columns:
        if isinstance(col.type, db.Date):
            out[col.name] = str(getattr(obj, col.name))
        else:
            out[col.name] = getattr(obj, col.name)
    return out



def normalize(obj, *parents):
    '''
    Prend un objet mappé SQLAlchemy et le transforme en dictionnaire pour 
    être sérialisé en JSON.
    Le second paramêtre `parents` permet de compléter la normalisation
    avec les données des tables liées par une relation d'héritage.
    '''
    try:
        return obj.to_json()
    except AttributeError as e:
        out = _normalize(obj, obj.__table__.columns)
        for p in parents:
            out.update(_normalize(obj, p().__table__.columns))
        return out



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
        return Response(json.dumps(res), 
                status=status, mimetype='application/json')
    return _json_resp



def send_mail(subject, msg_body):
    '''
    envoie un mail aux administrateurs de l'application
    '''
    app = get_app()
    if not app.config['SEND_MAIL']:
        return

    msg = Message('[recrutement] %s' % subject,
            sender=app.config['MAIL_SENDER'],
            recipients=app.config['MAIL_DESTS']
            )
    msg.body = msg_body

    with app.app_context():
        mail.send(msg)

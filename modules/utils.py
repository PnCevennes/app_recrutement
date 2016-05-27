#coding: utf8
'''
Fonctions utilitaires
'''

from server import db
from functools import wraps
from flask import Response
import json


def normalize(obj):
    '''
    Prend un objet mappé SQLAlchemy et le transforme en dictionnaire pour
    être sérialisé en JSON
    '''
    try:
        return obj.to_json()
    except AttributeError:
        out = {}
        for col in obj.__table__.columns:
            if isinstance(col.type, db.Date):
                out[col.name] = str(getattr(obj, col.name))
            else:
                out[col.name] = getattr(obj, col.name)
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


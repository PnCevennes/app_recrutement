#coding: utf8
'''
Fonctions utilitaires
'''

from server import db
from functools import wraps
from flask import Response
import json



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
    except AttributeError:
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


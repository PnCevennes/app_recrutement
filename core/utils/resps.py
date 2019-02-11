"""
Fonctions de définition des différents types de réponses
"""
import json
from functools import wraps

from flask import Response
from werkzeug.datastructures import Headers


def csv_response(data, filename='export.csv'):
    '''
    Retourne les entêtes HTTP pour les fichiers CSV
    '''
    headers = Headers()
    headers.add('Content-Type', 'text/csv')
    headers.add('Content-Disposition', 'attachment', filename=filename)
    headers.add('Cache-Control', 'no-cache')
    return Response(data, headers=headers)


def vcard_response(data, filename='export.vcf'):
    '''
    Retourne les entêtes HTTP pour les fichiers VCARD
    '''
    headers = Headers()
    headers.add('Content-Type', 'text/plain')
    headers.add('Content-Disposition', 'attachment', filename='export.vcf')
    return Response(data, headers=headers)


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

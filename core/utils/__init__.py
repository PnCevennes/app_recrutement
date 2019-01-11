'''
Fonctions utilitaires
'''

from .mail import send_mail

from .resps import (
        csv_response,
        vcard_response,
        json_resp
        )

registered_modules = {}
registered_funcs = {}


def register_module(prefix, blueprint):
    '''
    Importe les routes d'un module dans l'application
    '''
    registered_modules[prefix] = blueprint





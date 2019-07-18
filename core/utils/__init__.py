'''
Fonctions utilitaires
'''

from .mail import send_mail  # noqa

from .resps import (
    csv_response,  # noqa
    vcard_response,  # noqa
    json_resp  # noqa
)

registered_modules = {}
registered_funcs = {}


def register_module(prefix, blueprint):
    '''
    Importe les routes d'un module dans l'application
    '''
    registered_modules[prefix] = blueprint

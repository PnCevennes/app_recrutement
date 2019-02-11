'''
Fonctions relatives à l'authentification
'''
import json
from functools import wraps

from flask import redirect, url_for, g, request
from sqlalchemy.orm.exc import NoResultFound

import config
from server import db
from core.utils import registered_funcs
from core.auth.models import AuthStatus


class AuthUser:
    '''
    Classe représentant un utilisateur avec son nom et les groupes auxquels il appartient
    '''
    def __init__(self, data=None):
        try:
            self.id = data['id']
            self.name = data['name']
            self.groups = data['groups']
            self.mail = data['mail']
            self.is_valid = True
        except TypeError:
            self.id = None
            self.name = None
            self.mail = None
            self.groups = []
            self.is_valid = False

    def has_group(self, group):
        return group in self.groups

    @property
    def is_admin(self):
        return any([x in self.groups for x in ['admin-tizoutis', 'Administrateurs']])

    def as_dict(self):
        return {
                'id': self.id,
                'name': self.name,
                'groups': self.groups,
                'mail': self.mail,
                'is_valid': self.is_valid
                }


from core.auth.backends import check_user_login, get_user_groups


def check_auth(groups=None):
    '''
    vérifie l'authentification de l'utilisateur
    '''
    def _check_auth(fn):
        @wraps(fn)
        def __check_auth(*args_, **kwargs_):
            token = request.headers.get('token', None)
            if token is None:
                token = request.args.get('token', None)
            if token is None:
                return {'err': 'not authentified'}, 403
            if token != config.ADMIN_DEBUG_TOKEN:
                try:
                    userinfo = db.session.query(AuthStatus).filter(AuthStatus.token == token).one()
                    userdata = json.loads(userinfo.userdata)
                    if groups is not None:
                        if not any(map(
                                lambda x: x in userdata['groups'],
                                groups + ['admin-tizoutis'])):
                            return {'err': 'invalid groups'}, 403
                except NoResultFound as err:
                    return {'err': 'invalid auth'}, 403
            return fn(*args_, **kwargs_)


        return __check_auth
    return _check_auth


registered_funcs['check_auth'] = check_auth

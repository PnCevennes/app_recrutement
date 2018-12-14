'''
Fonctions relatives à l'authentification LDAP
'''
import json
from functools import wraps

import ldap3
from flask import redirect, url_for, g, request
from sqlalchemy.orm.exc import NoResultFound

import config
from server import db
from core.utils import registered_funcs
from core.auth.models import AuthStatus, User

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


class InvalidAuthError(Exception):
    '''
    Exception levée en cas d'erreur d'authentification
    '''
    pass


def check_auth(groups=None):
    '''
    vérifie l'authentification de l'utilisateur
    '''
    def _check_auth(fn):
        @wraps(fn)
        def __check_auth(*args_, **kwargs_):
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
                    else:
                        print('groups ok')
                except NoResultFound as err:
                    return {'err': 'invalid auth'}, 403
            return fn(*args_, **kwargs_)


        return __check_auth
    return _check_auth

registered_funcs['check_auth'] = check_auth


def ldap_connect(login, passwd):
    '''
    fonction de connexion au LDAP pour vérification des logins utilisateurs
    '''
    ldap_srv = ldap3.Server(
            'apollon.pnc.int',
            get_info=ldap3.ALL)

    ldap_cnx = ldap3.Connection(
            ldap_srv,
            user= config.LDAP_PREFIX % login,
            password=passwd,
            authentication=ldap3.NTLM)

    if ldap_cnx.bind():
        return ldap_cnx

    raise InvalidAuthError


def check_db_auth(login, passwd):
    try:
        user = db.session.query(User).filter(User.login==login).one()
    except NoResultFound:
        raise InvalidAuthError
    else:
        if not user.check_password(passwd):
            raise InvalidAuthError
        return AuthUser(user.to_json())



def check_ldap_auth(login, passwd):
    '''
    Vérifie les informations d'authentification sur le serveur LDAP
    et renvoie un objet AuthUser
    '''
    ldap_cnx = ldap_connect(login, passwd)
    ldap_cnx.search(
            config.LDAP_BASE_PATH,
            '(sAMAccountName=%s)' % login,
            attributes=['objectSid', 'cn', 'memberOf', 'mail'])
    user_data = ldap_cnx.entries[0]
    user_name = str(user_data.cn)
    user_groups = get_user_groups(user_data)
    user = AuthUser({
            'id': str(user_data.objectSid)[-4:],
            'name': user_name,
            'groups': user_groups,
            'mail': str(user_data.mail)
            })

    return user


def get_user_groups(user_data):
    '''
    Retourne la liste des groupes de l'utilisateur.
    '''
    user_groups = []
    if 'memberOf' in str(user_data):
        for grp in user_data['memberOf']:
            user_groups.append(
                    [gr[1] for gr in ldap3.utils.dn.parse_dn(grp)][0])
    return user_groups

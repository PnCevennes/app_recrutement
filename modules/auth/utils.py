'''
Fonctions relatives à l'authentification LDAP
'''

from functools import wraps

import ldap3
from flask import redirect, url_for, g

import config
from ..utils import registered_funcs

class AuthUser:
    '''
    Classe représentant un utilisateur avec son nom et les groupes auxquels il appartient
    '''
    def __init__(self, data=None):
        try:
            self.name = data['name']
            self.groups = data['groups']
            self.is_valid = True
        except TypeError:
            self.name = None
            self.groups = []
            self.is_valid = False

    def has_group(self, group):
        return group in self.groups

    @property
    def is_admin(self):
        return any([x in self.groups for x in ['admin-intranet', 'Administrateurs']])

    def as_dict(self):
        return {
                'name': self.name,
                'groups': self.groups,
                'is_valid': self.is_valid
                }


class InvalidAuthError(Exception):
    '''
    Exception levée en cas d'erreur d'authentification
    '''
    pass


def check_auth(*args, **kwargs):
    return True

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



def check_ldap_auth(login, passwd):
    '''
    Vérifie les informations d'authentification et renvoie un objet AuthUser
    '''
    ldap_cnx = ldap_connect(login, passwd)
    ldap_cnx.search(
            config.LDAP_BASE_PATH,
            '(sAMAccountName=%s)' % login,
            attributes=['cn', 'memberOf'])
    user_data = ldap_cnx.entries[0]
    user_name = str(user_data.cn)
    user_groups = get_user_groups(user_data)
    user = AuthUser({
            'name': user_name,
            'groups': user_groups
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


def require_valid_user(view):
    '''
    Décorateur pour les vues qui nécéssitent l'authentification préalable de l'utilisateur.
    '''
    @wraps(view)
    def _require_valid_user(*args, **kwargs):
        if not g.user.is_valid:
            return redirect(url_for('main.login_view'))
        return view(*args, **kwargs)
    return _require_valid_user


'''
Fonctions d'authentification via annuaire LDAP
'''
import ldap3
import config
from core.auth.utils import AuthUser
from core.auth.exc import InvalidAuthError


def ldap_connect(login, passwd):
    '''
    fonction de connexion au LDAP pour vérification des logins utilisateurs
    '''
    ldap_srv = ldap3.Server(
        config.LDAP_SERVER,
        get_info=ldap3.ALL)

    ldap_cnx = ldap3.Connection(
        ldap_srv,
        user=config.LDAP_PREFIX % login,
        password=passwd,
        authentication=ldap3.NTLM)

    if ldap_cnx.bind():
        return ldap_cnx

    raise InvalidAuthError


def check_user_login(login, passwd):
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
                [gr[1] for gr in ldap3.utils.dn.parse_dn(grp)][0]
            )
    return user_groups


def get_members(groups):
    '''
    Retourne la liste des membres d'un groupe
    '''
    ldap_cnx = ldap_connect(
        config.LDAP_USER,
        config.LDAP_PASS)
    ldap_cnx.search(
        'ou=Personnel,dc=pnc,dc=int',
        '(sn=*)',
        attributes=['cn', 'mail', 'memberOf'])
    for entry in ldap_cnx.entries:
        user_groups = get_user_groups(entry)
        for grp in groups:
            if grp in user_groups:
                yield entry
                break


def get_members_mails(groups):
    '''
    Retourne l'adresse email des membres d'un groupe
    '''
    yield from [str(member.mail) for member in get_members(groups)]

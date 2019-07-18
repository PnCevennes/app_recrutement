"""
Mise a disposition des fonctions de gestion des utilisateurs
correspondantes à la configuration demandée
"""
import config


if config.AUTH_TYPE == 'ldap':
    from core.auth.backends.ldap import (
        check_user_login,
        get_user_groups,
        get_members,
        get_members_mails
    )
else:
    from core.auth.backends.database import (
        check_user_login,
        get_user_groups,
        get_members,
        get_members_mails
    )

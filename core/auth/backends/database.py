from sqlalchemy.orm.exc import NoResultFound

from server import db
from core.auth.utils import AuthUser
from core.auth.models import User
from core.auth.exc import InvalidAuthError


def check_user_login(login, passwd):
    try:
        user = db.session.query(User).filter(User.login==login).one()
    except NoResultFound:
        raise InvalidAuthError
    else:
        if not user.check_password(passwd):
            raise InvalidAuthError
        return AuthUser(user.to_json())


def get_user_groups(user_data):
    return [grp.label for grp in user_data.groups]

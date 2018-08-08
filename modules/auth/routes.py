'''
routes relatives aux application, utilisateurs et à l'authentification
'''

import json
import datetime
import uuid
from functools import wraps

from flask import (
        Blueprint,
        request,
        g,
        Response)
from sqlalchemy.orm.exc import NoResultFound

import config
from server import get_app
from server import db as _db
from . import models, utils
from ..utils import normalize, json_resp, register_module, registered_funcs


class InvalidAuth(Exception):
    pass

routes = Blueprint('auth', __name__)

register_module('/auth', routes)

@routes.route('/login', methods=['POST'])
@json_resp
def login_view():
    login = request.json['login'].strip()
    passwd = request.json['passwd'].strip()


    try:
        user = utils.check_ldap_auth(login, passwd)
        userdata = json.dumps(user.as_dict())
        token = uuid.uuid4().hex
        expiration = datetime.date.today() + datetime.timedelta(days=1)
        authstatus = _db.session.query(models.AuthStatus).get(user.id)

        if authstatus:
            authstatus.token = token
            authstatus.expiration = expiration
            authstatus.userdata = userdata
            _db.session.commit()

        else:
            authstatus = models.AuthStatus(
                    user_id=user.id,
                    token=token,
                    expiration=expiration,
                    userdata=userdata
                    )
            _db.session.add(authstatus)
            _db.session.commit()

        return authstatus.as_dict()
    except utils.InvalidAuthError as err:
        return Response('[]', 403)


@routes.route('/reconnect', methods=['POST'])
@json_resp
def reconnect_view():
    token = request.json['token']
    uid = request.json['id']
    now = datetime.date.today()
    authstatus = _db.session.query(models.AuthStatus).get(uid)
    if not authstatus:
        return {'err': 'invalid user'}, 403
    if not authstatus.token == token:
        return {'err': 'invalid token'}, 403
    if authstatus.expiration < now:
        return {'err': 'expired'}, 403
    # authstatus.token = uuid.uuid4().hex
    authstatus.expiration = now + datetime.timedelta(days=1)
    _db.session.commit()
    return authstatus.as_dict()




@routes.route('/logout')
@json_resp
def logout():
    token = request.json['token'].strip()
    uid = request.json['id'].strip()
    authstatus = _db.session.query(AuthStatus).get(uid)
    if authstatus:
        _db.session.delete(authstatus)
    return []


@routes.route('/users', methods=['GET'])
@json_resp
def get_users():
    users = models.User.query.all()
    return [normalize(user) for user in users]


@routes.route('/user/<id_user>', methods=['GET'])
@json_resp
def get_user(id_user):
    user = models.User.query.get(id_user)
    if not user:
        return [], 404
    return normalize(user)

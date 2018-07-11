'''
routes relatives aux application, utilisateurs et à l'authentification
'''

import json
import datetime
from functools import wraps
from flask import (
        Blueprint,
        request,
        g,
        Response,
        current_app)
from sqlalchemy.orm.exc import NoResultFound
from itsdangerous import (
        TimedSerializer,
        SignatureExpired,
        BadSignature)
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
def login_view():
    login = request.json['login'].strip()
    passwd = request.json['passwd'].strip()

    try:
        user = utils.check_ldap_auth(login, passwd)

        serializer = TimedSerializer(config.SECRET_KEY)
        cookie_data = serializer.dumps(user.as_dict())
        cookie_exp = datetime.datetime.now() + datetime.timedelta(days=1)

        resp = current_app.make_response(json.dumps(user.as_dict()))
        resp.set_cookie('user', cookie_data, expires=cookie_exp)

        return resp
    except utils.InvalidAuthError as err:
        return Response('[]', 403)



@routes.route('/logout')
def logout():
    resp = Response(json.dumps({'logout': True}))
    resp.set_cookie('token', '')
    return resp


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

@routes.route('/reconnect', methods=['GET'])
@json_resp
def reconnect():
    try:
        serializer = TimedSerializer(config.SECRET_KEY)
        user = serializer.loads(request.cookies.get('user', {}))
        print(user)
        return {'user': user}
    except SignatureExpired:
        print('expired')
        return [], 403
    except BadSignature:
        print('bad signature')
        return [], 403

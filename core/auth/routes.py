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
from server import get_app, db as _db
from core.utils import (
        json_resp,
        register_module,
        registered_funcs)
from . import models, utils
from .serializers import UserSerializer, UserFullSerializer
from .exc import InvalidAuthError


routes = Blueprint('auth', __name__)

register_module('/auth', routes)


@routes.route('/login', methods=['POST'])
@json_resp
def login_view():
    '''
    Connexion de l'utilisateur
    '''
    login = request.json['login'].strip()
    passwd = request.json['passwd'].strip()

    try:
        user = utils.check_user_login(login, passwd)
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
    except InvalidAuthError as err:
        return Response('[]', 403)


@routes.route('/reconnect', methods=['POST'])
@json_resp
def reconnect_view():
    '''
    Reconnexion de l'utilisateur si le jeton est encore valide
    '''
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
    '''
    Déconnexion de l'utilisateur
    '''
    token = request.json['token'].strip()
    uid = request.json['id'].strip()
    authstatus = _db.session.query(AuthStatus).get(uid)
    if authstatus:
        _db.session.delete(authstatus)
    return []


@routes.route('/users/', methods=['GET'])
@json_resp
def get_users():
    '''
    Liste des utilisateurs
    '''
    users = _db.session.query(models.User).all()
    return [UserSerializer(user).serialize() for user in users]


@routes.route('/users/<id_user>', methods=['GET'])
@json_resp
def get_user(id_user):
    '''
    Détail d'un utilisateur
    '''
    user = _db.session.query(models.User).get(id_user)
    if not user:
        return [], 404
    return UserFullSerializer(user).serialize()


@routes.route('/groups', methods=['GET'])
@json_resp
def get_groups():
    '''
    Liste des groupes
    '''
    groups = _db.session.query(models.Group).all()
    return [{'id': group.id, 'name': group.name} for group in groups]


@routes.route('/groups/<id_group>', methods=['GET'])
@json_resp
def get_group(id_group):
    '''
    Détail d'un groupe
    '''
    group = _db.session.query(models.Group).get(id_group)
    if not group:
        return [], 404
    return group.to_json()


@routes.route('/users/', methods=['POST', 'PUT'])
@json_resp
@utils.check_auth(groups=['admin-tizoutis'])
def create_user():
    data = request.json
    # chargement des groupes
    groups = _db.session.query(models.Group).filter(
            models.Group.name.in_(data.get('groups', []))
            ).all()
    data['groups'] = groups
    user = models.User()
    serialize = UserFullSerializer(user)
    serialize.populate(data)
    _db.session.add(user)
    _db.session.commit()
    return [serialize.serialize()]


@routes.route('/users/<id_user>', methods=['POST', 'PUT'])
@json_resp
@utils.check_auth(groups=['admin-tizoutis'])
def update_user(id_user):
    data = request.json
    # chargement des groupes
    groups = _db.session.query(models.Group).filter(
            models.Group.name.in_(data.get('groups', []))
            ).all()
    data['groups'] = groups
    if not len(data['password']):
        del(data['password'])
    user = _db.session.query(models.User).get(id_user)
    if not user:
        return [], 404
    serialize = UserFullSerializer(user)
    serialize.populate(data)
    _db.session.commit()
    return [serialize.serialize()]


@routes.route('/users/<id_user>', methods=['DELETE'])
@json_resp
@utils.check_auth(groups=['admin-tizoutis'])
def delete_user(id_user):
    user = _db.session.query(models.User).get(id_user)
    if not user:
        return [], 404
    _db.session.delete(user)
    return {'id': id_user}

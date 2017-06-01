#coding: utf8

'''
routes relatives aux application, utilisateurs et à l'authentification
'''

import json
import uuid
import datetime
from functools import wraps
from flask import Blueprint, request, g, Response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from itsdangerous import (
        TimedJSONWebSignatureSerializer as Serializer,
        SignatureExpired,
        BadSignature)
from server import get_app
from . import models
from ..utils import normalize, json_resp, register_module, registered_funcs

_db = SQLAlchemy()

class InvalidAuth(Exception):
    pass

routes = Blueprint('auth', __name__)

register_module('/auth', routes)


def check_auth(app_id, level, final=True):
    def _check_auth(fn):
        @wraps(fn)
        def __check_auth(*args, **kwargs):
            g.user_is_authorized = True
            try:
                serializer = Serializer(get_app().config['SECRET_KEY'])
                user = serializer.loads(request.cookies.get('token', {}))
                app = list(filter(lambda x: x.application_id == app_id,
                        user.applications))
                if app[0].niveau<level:
                    if final:
                        raise InvalidAuth
                    else:
                        g.user_is_authorized = False
                g.authenticated_user = user
                return fn(*args, **kwargs)
            except SignatureExpired as e:
                return [], 403
            except BadSignature as e:
                return [], 403
            except InvalidAuth as e:
                return [], 403
        return __check_auth
    return _check_auth
registered_funcs['check_auth'] = check_auth


@routes.route('/reconnect', methods=['GET'])
@json_resp
def reconnect():
    try:
        serializer = Serializer(get_app().config['SECRET_KEY'])
        user = serializer.loads(request.cookies.get('token', {}))
        return {'user': user}
    except SignatureExpired as e:
        return [], 403
    except BadSignature as e:
        return [], 403



@routes.route('/login', methods=['POST'])
def login():
    try:
        user_data = request.json
        user = models.User.query.filter(models.User.login==user_data['login']).one()
        if not user.check_password(user_data['password']):
            raise InvalidAuth
        serializer = Serializer(get_app().config['SECRET_KEY'])
        cookie_data = serializer.dumps(user.to_json())
        cookie_exp = datetime.datetime.now() + datetime.timedelta(days=1)

        resp = Response(
                json.dumps({'login':True, 'user': normalize(user)}),
                mimetype='application/json'
                )
        resp.set_cookie('token', cookie_data, expires=cookie_exp)
        return resp
    except NoResultFound as e:
        return Response(
                json.dumps(
                    {'login': False, 'msg': 'Utilisateur inconnu'}),
                    status=403)
    except InvalidAuth as e:
        return Response(
                json.dumps(
                    {'login': False, 'msg': 'Utilisateur inconnu'}),
                    status=403)
    except Exception as e:
        return Response(
                json.dumps(
                    {'login': False, 'msg': 'Données corrompues'}),
                    status=400)



@routes.route('/logout')
def logout():
    resp = Response(json.dumps({'logout': True}))
    resp.set_cookie('token', '')
    return resp


@routes.route('/')
def auth():
    return 'authentification'


@routes.route('/applications', methods=['GET'])
@json_resp
def get_applications():
    app_list = models.Application.query.all()
    return [normalize(item) for item in app_list]


@routes.route('/application/<app_id>', methods=['GET'])
@json_resp
def get_application(app_id):
    app = models.Application.query.get(app_id)
    if not app:
        return [], 404
    return normalize(app)


@routes.route('/application', methods=['POST', 'PUT'])
@json_resp
def create_application():
    try:
        app_data = request.json
        app = models.Application(**app_data)
        _db.session.add(app)
        _db.session.commit()
        return normalize(app)
    except:
        return []


@routes.route('/application/<id_app>', methods=['POST', 'PUT'])
@json_resp
def update_application(id_app):
    try:
        app_data = request.json
        app = models.Application.get(app_data['id'])
        if not app:
            return [], 404
        for field, value in app_data.items():
            setattr(app, field, value)
        _db.session.commit()
        return normalize(app)
    except:
        return [], 400


@routes.route('/application/<id_app>', methods=['DELETE'])
@json_resp
def delete_application(id_app):
    app = models.Application.get(app_id)
    if not app:
        return [], 404
    _db.session.delete(app)
    _db.session.commit()
    return normalize(app)


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


@routes.route('/user', methods=['POST', 'PUT'])
@json_resp
def create_user():
    try:
        user_data = request.json
        print(user_data)
        apps = user_data.pop('applications', [])
        is_admin = user_data.pop('admin', False)
        user = models.User(**user_data)
        _db.session.add(user)
        rels = []
        for app in apps:
            rels.append(models.AppUser(
                    application_id=app['id'],
                    user=user,
                    niveau=app['niveau']))
        _db.session.add_all(rels)
        _db.session.commit()



        return normalize(user)
    except:
        return [], 400


@routes.route('/user/<id_user>', methods=['POST', 'PUT'])
@json_resp
def update_user(id_user):
    try:
        user_data = request.json
        apps = user_data.pop('applications', [])
        id_admin = user_data.pop('admin', False)
        user = models.User.query.get(user_data['id'])
        if not user:
            return [], 404
        for key, value in user_data.items():
            setattr(user, key, value)
        rels = []
        for app in apps:
            rel = list(filter(lambda x: x.application_id==app['id'], user.relations))
            if not len(rel):
                apprel = models.AppUser(
                        application_id=app['id'],
                        user=user,
                        niveau=app['niveau'])
                _db.session.add(apprel)
            else:
                rel[0].niveau = app['niveau']

        _db.session.commit()
        return normalize(user)
    except Exception as e:
        print(e)
        return [], 400


@routes.route('/user/<id_user>', methods=['DELETE'])
@json_resp
def delete_user(id_user):
    user = models.User.query.get(id_user)
    if not user:
        return [], 404
    for rel in user.relations:
        _db.session.delete(rel)
    _db.session.delete(user)
    _db.session.commit()
    return []

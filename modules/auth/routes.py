#coding: utf8

'''
routes relatives aux application, utilisateurs et à l'authentification
'''

from flask import Blueprint
from . import models
from ..utils import normalize, json_resp, register_module


routes = Blueprint('auth', __name__)

register_module('/auth', routes)


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
    #TODO
    return []


@routes.route('/application/<id_app>', methods=['POST', 'PUT'])
@json_resp
def update_application():
    #TODO
    return []


@routes.route('/application/<id_app>', methods=['DELETE'])
@json_resp
def delete_application():
    #TODO
    return []


@routes.route('/users', methods=['GET'])
@json_resp
def get_users():
    #TODO
    return []


@routes.route('/user/<id_user>', methods=['GET'])
@json_resp
def get_user(id_user):
    #TODO
    return []


@routes.route('/user', methods=['POST', 'PUT'])
@json_resp
def create_user():
    #TODO
    return []


@routes.route('/user/<id_user>', methods=['POST', 'PUT'])
@json_resp
def update_user():
    #TODO
    return []


@routes.route('/user/<id_user>', methods=['DELETE'])
@json_resp
def delete_user():
    #TODO
    return []

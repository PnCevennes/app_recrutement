#coding: utf8

'''
Routes de base
'''

import os
import os.path
import mimetypes

from flask import Blueprint, request, current_app, Response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import InvalidRequestError
from werkzeug.utils import secure_filename
from modules.utils import json_resp
from models import Fichier

main = Blueprint('main', __name__)
db = SQLAlchemy()


@main.route('/')
def index():
    with open('./static/app.htm', 'r') as fp:
        return fp.read()


@main.route('/upload', methods=['POST'])
@json_resp
def upload():
    if not 'fichier' in request.files:
        return {}, 400
    fichier = request.files['fichier']
    fname = secure_filename(fichier.filename)
    file_data = Fichier(filename=fname)
    try:
        db.session.add(file_data)
        db.session.flush()
        db.session.commit()
        fichier.save(os.path.join('.', current_app.config['UPLOAD_DIR'], file_data.get_file_uri()))
    except InvalidRequestError as e:
        db.session.rollback()
        return {'msg': 'DB Locked'}, 400
    return {'filename': fname,
            'file_uri': file_data.get_file_uri(),
            'id': file_data.id}


@main.route('/upload/<file_uri>', methods=['GET'])
def get_uploaded_file(file_uri):
    file_ = os.path.join(current_app.config['UPLOAD_DIR'], file_uri)
    mimetype_, encoding = mimetypes.guess_type(file_)
    with open(file_, 'rb') as fp:
        return Response(fp.read(), mimetype=mimetype_)
    return ''


@main.route('/upload/<fileid>', methods=['DELETE'])
@json_resp
def vdelete_uploaded_file(fileid):
    return delete_file(fileid)


def delete_file(fileid):
    try:
        fich = db.session.query(Fichier).get(fileid)
        file_uri = fich.get_file_uri()
        db.session.delete(fich)
        db.session.flush()
        db.session.commit()
        os.unlink(os.path.join('.', current_app.config['UPLOAD_DIR'], file_uri))
        return {}, 200
    except Exception as e:
        db.session.rollback()
        return {'err': str(e)}, 400

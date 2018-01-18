'''
Routes de base
'''

import os
import os.path
import mimetypes

from flask import Blueprint, request, current_app, Response
from sqlalchemy.exc import InvalidRequestError
from werkzeug.utils import secure_filename
from server import db as _db
from modules.utils import json_resp
from models import Fichier


main = Blueprint('main', __name__)


@main.route('/')
def index():
    with open('./static/app.htm', 'r') as fp:
        return fp.read()


@main.route('/upload', methods=['POST'])
@json_resp
def vupload_file():
    if 'fichier' not in request.files:
        return {}, 400
    return upload_file(request.files['fichier'])


def upload_file(fichier, path=None):
    if path is None:
        path = current_app.config['UPLOAD_DIR']
    fname = secure_filename(fichier.filename)
    file_data = Fichier(filename=fname)
    try:
        _db.session.add(file_data)
        _db.session.flush()
        _db.session.commit()
        fichier.save(os.path.join(path, file_data.file_uri))
    except InvalidRequestError as e:  # noqa
        _db.session.rollback()
        import traceback
        return {'msg': traceback.format_exc()}, 400
    return {'filename': fname,
            'file_uri': file_data.file_uri,
            'id': file_data.id}


@main.route('/upload/<file_uri>', methods=['GET'])
def vget_uploaded_file(file_uri):
    return get_uploaded_file(file_uri)


def get_uploaded_file(file_uri, path=None):
    if path is None:
        path = current_app.config['UPLOAD_DIR']

    file_ = os.path.join(path, file_uri)
    mimetype_, encoding = mimetypes.guess_type(file_)
    with open(file_, 'rb') as fp:
        return Response(fp.read(), mimetype=mimetype_)
    return Response('', status=404)


@main.route('/upload/<fileid>', methods=['DELETE'])
@json_resp
def vdelete_uploaded_file(fileid):
    return delete_uploaded_file(fileid)


def delete_uploaded_file(fileid, path=None, db=None):
    if path is None:
        path = current_app.config['UPLOAD_DIR']
    if db is None:
        db = _db

    try:
        fich = db.session.query(Fichier).get(fileid)
        file_uri = fich.get_file_uri()
        db.session.delete(fich)
        db.session.flush()
        db.session.commit()
        os.unlink(os.path.join(path, file_uri))
        return {}, 200
    except Exception as e:  # noqa
        db.session.rollback()
        import traceback
        return {'err': traceback.format_exc()}, 400

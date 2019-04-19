import os.path
import rtfunicode

from flask import Response, current_app
from werkzeug.datastructures import Headers

from server import db
from .models import SubvTemplate


def render(templatename, filename, data):
    tpl = db.session.query(SubvTemplate).filter(SubvTemplate.name == templatename).one()
    with open(tpl.path, 'r') as fp:
        template = fp.read().encode('ascii')
        for varname, value in data.items():
            varmod = b'#%s#' % varname.encode('ascii')
            template = template.replace(varmod, str(value).encode('rtfunicode') if value and len(str(value)) else b'')

    headers = Headers()
    headers.add('Content-Type', 'text/rtf')
    headers.add('Content-Disposition', 'attachment', filename=filename)
    headers.add('Cache-Control', 'no-cache')
    return Response(template, headers=headers)

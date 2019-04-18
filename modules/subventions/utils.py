import os.path
import rtfunicode

from flask import Response, current_app
from werkzeug.datastructures import Headers


def render(templatename, filename, data):
    path = current_app.config['TEMPLATES_DIR']
    with open(os.path.join(path, templatename), 'r') as fp:
        template = fp.read().encode('ascii')
        for varname, value in data.items():
            varmod = b'#%s#' % varname.encode('ascii')
            template = template.replace(varmod, str(value).encode('rtfunicode') if value and len(str(value)) else b'')

    headers = Headers()
    headers.add('Content-Type', 'text/rtf')
    headers.add('Content-Disposition', 'attachment', filename=filename)
    headers.add('Cache-Control', 'no-cache')
    return Response(template, headers=headers)

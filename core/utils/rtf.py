import rtfunicode
from flask import Response
from werkzeug.datastructures import Headers

def render_rtf(template_name, template_path, data):
    '''
    Génère un document RTF à partir d'un modèle et d'un jeu de données
    '''
    with open(template_path, 'r') as fp:
        template = fp.read().encode('ascii')
        for varname, value in data.items():
            varmod = b'#' + varname.encode('ascii') + b'#'
            value = (str(value).encode('rtfunicode')
                     if value and len(str(value)) else b'')
            template = template.replace(varmod, value, -1)

    headers = Headers()
    headers.add('Content-Type', 'text/rtf')
    headers.add(
        'Content-Disposition',
        'attachment',
        filename='%s.rtf' % template_name
    )
    headers.add('Cache-Control', 'no-cache')
    return Response(template, headers=headers)

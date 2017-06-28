import json

from flask import Blueprint
from modules.utils import json_resp, register_module
#from . import utils

routes = Blueprint('superv', __name__)

register_module('/supervision', routes)

@routes.route('/data')
@json_resp
def sup_index():
    with open('resources/sup_out.json', 'r') as fp:
        return json.load(fp)

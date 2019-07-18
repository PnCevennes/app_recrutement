'''
from .annuaire import routes
from .interventions import routes
from .recrutement import routes
from .supervision import routes
from .travaux_batiments import routes
from .subventions import routes
'''

import os
import os.path

here = os.path.dirname(__file__)
for item in os.listdir(here):
    if not item.startswith('_'):
        __import__('modules.%s.routes' % item)

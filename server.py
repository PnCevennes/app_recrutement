'''
Démarrage de l'application
'''
import os
import atexit

import flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail


db = SQLAlchemy()
mail = Mail()
cors = CORS()

app_globals = {}

def get_app():
    if app_globals.get('app', False):
        return app_globals['app']
    app = flask.Flask(__name__)
    app.config.from_pyfile('./config.py')
    db.init_app(app)
    mail.init_app(app)
    cors.init_app(app)

    from core.utils import registered_modules
    from core import routes
    import modules

    app.register_blueprint(routes.main)

    for prefix, blueprint in registered_modules.items():
        app.register_blueprint(blueprint, url_prefix=prefix)

    app_globals['app'] = app

    if app.config.get('ENABLE_SUPERVISION', False):
        from modules.supervision.tools import Scanner, shutdown_fn
        scan = Scanner()

        atexit.register(shutdown_fn, scan)

    return app



if __name__ == '__main__':
    app = get_app()
    from flask_script import Manager
    Manager(app).run()

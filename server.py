#coding: utf8

'''
Démarrage de l'application
'''


import flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

db = SQLAlchemy()
mail = Mail()

app_globals = {}


def get_app():
    if app_globals.get('app', False):
        return app_globals['app']
    app = flask.Flask(__name__)
    app.config.from_pyfile('./config.py')
    db.init_app(app)
    mail.init_app(app)

    @app.route('/', methods=['GET'])
    def index():
        with app.open_resource('static/app.htm') as f:
            return f.read()


    import routes
    app.register_blueprint(routes.main)

    from modules.utils import registered_modules
    for prefix, blueprint in registered_modules.items():
        app.register_blueprint(blueprint, url_prefix=prefix)

    app_globals['app'] = app

    return app

app = get_app()


if __name__ == '__main__':
    from flask.ext.script import Manager
    Manager(app).run()


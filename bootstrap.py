#coding: utf8

'''
Fichier de démarrage alternatif, utile pour une connexion console à
l'application.

$ python bootstrap.py shell
'''


from flask.ext.script import Manager
from server import get_app

manager = Manager(get_app())

if __name__ == '__main__':
    manager.run()

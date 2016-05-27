#coding: utf8

'''
Routes de base
'''

from flask import Blueprint

main = Blueprint('main', __name__)



@main.route('/')
def index():
    return 'Ça marche !'


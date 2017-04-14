#coding: utf8

'''
Routes de base
'''

from flask import Blueprint, g

main = Blueprint('main', __name__)



@main.route('/')
def index():
    with open('./static/app.htm', 'r') as fp:
        return fp.read()

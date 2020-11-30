import atexit
import os

def shutdown_fn():
    '''
    Stoppe le thread de scan des serveurs et supprime le
    fichier lock qui empèche la multiplication des threads
    lorsqu'il y a plusieurs workers en prod
    '''
    os.unlink('./supervision.lock')
    print('QUIT')

atexit.register(shutdown_fn)

with open('./supervision.lock', 'w') as fp:
    fp.write('supervision')

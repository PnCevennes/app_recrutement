import atexit

def shutdown_fn():
    '''
    Stoppe le thread de scan des serveurs et supprime le
    fichier lock qui empèche la multiplication des threads
    lorsqu'il y a plusieurs workers en prod
    '''
    os.unlink('./supervision.lock')
    print('QUIT')

atexit.register(shutdown_fn, scan)

with open('./supervision.lock') as fp:
    fp.write('supervision')

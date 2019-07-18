import subprocess
import threading
import datetime
import os
import os.path

from sqlalchemy.orm.exc import ObjectDeletedError


def create_evt_equip(equip_id, evt_type):
    '''
    Crée un evenement sur un équipement
    equip_id : id de l'equipement
    evt_type : 0 down, 1 up
    '''
    from .models import EvtEquipement
    evt = EvtEquipement()
    evt.equip_id = equip_id
    evt.evt_type = evt_type
    evt.evt_date = datetime.datetime.now()
    return evt


def shutdown_fn(scan):
    '''
    Stoppe le thread de scan des serveurs et supprime le
    fichier lock qui empèche la multiplication des threads
    lorsqu'il y a plusieurs workers en prod
    '''
    scan.evt.set()
    os.unlink('./supervision.lock')
    print('QUIT')


def scan_ping(ip):
    '''
    retourne l'accessibilité de l'équipement réseau par PING
    '''
    res = subprocess.Popen(
        ['fping', ip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if res.wait():
        return False
    else:
        return b'alive' in res.stdout.read()


def _scan(app, session, evt):
    '''
    Thread qui scanne les différents équipements réseau.
    '''
    from .models import Equipement, EquipementSerializer
    with app.app_context():
        counter = 0
        while not evt.is_set():
            print('nouvelle boucle')
            if counter % app.config['SUP_INTERVAL'] == 0:
                counter = 0
                print('nouveau scan')
                try:
                    equips = session.query(Equipement).all()
                    for equip in equips:
                        # compat 3.4
                        if not scan_ping(equip.ip_addr):
                            if equip.status == 1:
                                eq_evt = create_evt_equip(equip.id, 0)
                                session.add(eq_evt)
                            equip.status = 0
                        else:
                            if equip.status == 0:
                                eq_evt = create_evt_equip(equip.id, 1)
                                session.add(eq_evt)
                            equip.status = 1
                            equip.last_up = datetime.datetime.now()
                        session.flush()
                        session.commit()
                except ObjectDeletedError:
                    print('objet supprimé rencontré')
            counter += 1
            evt.wait(60)


class Scanner:
    '''
    Lance le thread qui scanne les équipements réseau
    à intervalles réguliers.
    '''
    def __init__(self):
        from server import db, get_app
        self.app = get_app()
        self.session = db.session
        self.evt = threading.Event()
        if not os.path.exists('./supervision.lock'):
            # Si le fichier de verrouillage existe
            # Aucun thread supplémentaire n'est lancé
            with open('./supervision.lock', 'w'):
                # Ecriture du fichier de verrouillage lors du démarrage
                # du process de scan
                thr = threading.Thread(
                    target=_scan,
                    args=[self.app, self.session, self.evt]
                )
                thr.start()

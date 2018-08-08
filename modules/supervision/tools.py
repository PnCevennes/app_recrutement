import subprocess
import threading
import datetime
import os
import os.path


def _scan(app, session, evt):
    '''
    Thread qui scanne les différents équipements réseau.
    '''
    from .models import Equipement, EquipementSerializer
    with app.app_context():
        counter = 0
        while not evt.is_set():
            print('nouvelle boucle')
            equips = session.query(Equipement).all()
            out = []
            if counter % 3 == 0:
                counter = 0
                print('nouveau scan')
                for equip in equips:
                    res = subprocess.run(
                            ['fping', equip.ip_addr],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                    if len(res.stderr):
                        equip.status = 0
                    else:
                        equip.status = 1
                        equip.last_up = datetime.datetime.now()
                    out.append(EquipementSerializer(equip).serialize())
                    session.flush()
                    session.commit()
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
                thr = threading.Thread(target=_scan, args=[self.app, self.session, self.evt])
                thr.start()

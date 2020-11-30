import subprocess
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import SQLALCHEMY_DATABASE_URI, ENABLE_SUPERVISION
from modules.supervision.models import Equipement, EvtEquipement


db = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=db)

store = Session()

def scan(ip):
    '''
    ping l'adresse IP
    '''
    res = subprocess.Popen(
            ['fping', '-t', '100', ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )
    if res.wait():
        return False
    else:
        return b'alive' in res.stdout.read()


def scan_all():
    '''
    Charge la liste des équipements à tester et met à jour
    leur état en fonction du ping
    '''
    for equip in store.query(Equipement).all():
        # ping le serveur
        result = int(scan(equip.ip_addr))
        if result:
            # serveur UP, mise à jour de last_up
            equip.last_up = datetime.datetime.now()
        if result != equip.status:
            # changement dans l'état du serveur, création d'un évenement
            equip.status = result
            evt = EvtEquipement(
                    equip_id=equip.id,
                    evt_type=result,
                    evt_date=datetime.datetime.now())
            store.add(evt)
        store.commit()

if __name__ == '__main__':
    scan_all()

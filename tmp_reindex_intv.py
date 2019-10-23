from server import db
from core.models import get_chrono
from modules.interventions.models import Demande


def reindex_interventions():
    dems = db.session.query(Demande).all()

    for dem in dems:
        basechr = '{}I'.format(str(dem.dem_date.year)[2:4])
        chrono = get_chrono(basechr)
        dem.num_intv = chrono

    db.session.commit()

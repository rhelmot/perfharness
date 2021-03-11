import os

from sqlalchemy.sql import expression as ex

from . import db
from .config import load_config

def main(args):
    if len(args) == 0 or any(not os.path.exists(f) for f in args):
        print("Usage: python -m perfharness delete testcase [testcase ...]")
        return

    config = load_config()
    db.db_connect(config)

    files = [os.path.basename(f) for f in args]
    db.session.execute(ex.delete(db.Run).where(db.Run.testcase.in_(files)))

    db.db_close()
import random
import datetime
from typing import Optional

import sqlalchemy.ext.declarative
import sqlalchemy.orm

meta = sqlalchemy.MetaData()
Base = sqlalchemy.ext.declarative.declarative_base(metadata=meta)
session = None  # type: Optional[sqlalchemy.orm.Session]

class Run(Base):
    __tablename__ = 'runs'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    runtime = sqlalchemy.Column(sqlalchemy.Float)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime)
    note = sqlalchemy.Column(sqlalchemy.String)
    testcase = sqlalchemy.Column(sqlalchemy.String(100))
    testcase_hash = sqlalchemy.Column(sqlalchemy.String(128))
    codebase_hash = sqlalchemy.Column(sqlalchemy.String(128))

    python = sqlalchemy.Column(sqlalchemy.String(20))
    hostname = sqlalchemy.Column(sqlalchemy.String(50))
    os = sqlalchemy.Column(sqlalchemy.String(20))
    cpu = sqlalchemy.Column(sqlalchemy.String(100))
    cpu_count = sqlalchemy.Column(sqlalchemy.String(10))
    memory_size = sqlalchemy.Column(sqlalchemy.String(10))

    @classmethod
    def record_test(cls, testcase, testcase_hash, runtime, codebase_hash, machine):
        session.add(Run(id=random.randrange(0, 100000000), runtime=runtime, timestamp=datetime.datetime.now(),
                        testcase=testcase, testcase_hash=testcase_hash, codebase_hash=codebase_hash, **machine))


def db_connect(config):
    global session
    if session is None:
        engine = sqlalchemy.create_engine(config['database'])
        session = sqlalchemy.orm.sessionmaker(bind=engine)()
        meta.create_all(engine)

def db_close():
    global session
    session.commit()
    session.close()
    session = None

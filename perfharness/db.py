import random
import datetime
import ssl

import sqlalchemy.ext.declarative
import sqlalchemy.orm

try:
    import psycopg2
except ImportError:
    try:
        from psycopg2cffi import compat
        compat.register()
    except ImportError:
        pass

meta = sqlalchemy.MetaData()
Base = sqlalchemy.ext.declarative.declarative_base(metadata=meta)
session: sqlalchemy.orm.Session | None = None
engine: sqlalchemy.engine.Engine | None = None

def get_engine():
    assert engine is not None
    return engine

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
    def record_test(cls, testcase, testcase_hash, runtime, codebase_hash, machine, note):
        if session is None:
            raise Exception("Not connected to database")
        session.add(Run(id=random.randrange(0, 100000000), runtime=runtime, timestamp=datetime.datetime.now(),
                        testcase=testcase, testcase_hash=testcase_hash, codebase_hash=codebase_hash,
                        note=note, **machine))
        session.commit()


def db_connect(config, create_session=True):
    global session, engine
    if engine is None:
        connect_args = {}
        if 'database_ssl_param' in config or 'database_ssl_rootcrt' in config or 'database_ssl_clientcrt' in config or 'database_ssl_clientkey' in config:
            if 'database_ssl_param' not in config or 'database_ssl_rootcrt' not in config or 'database_ssl_clientcrt' not in config or 'database_ssl_clientkey' not in config:
                raise ValueError("Must provide all database ssl parameters or none of them")
            ssl_context = ssl.create_default_context(cafile=config['database_ssl_rootcrt'])
            ssl_context.load_cert_chain(certfile=config['database_ssl_clientcrt'], keyfile=config['database_ssl_clientkey'])
            connect_args[config['database_ssl_param']] = ssl_context

        engine = sqlalchemy.create_engine(config['database'], connect_args=connect_args)
    if session is None and create_session:
        session = sqlalchemy.orm.sessionmaker(bind=engine)()
        meta.create_all(engine)

def db_close():
    global session
    if session is None:
        return

    session.commit()
    session.close()
    session = None

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class DatabaseInitializer:
    def __init__(self, base) -> None:
        self.base = base

    def init_database(self, postgres_dsn):
        engine = create_engine(f'{postgres_dsn}'.format(postgres_dsn=postgres_dsn))
        # TODO если engine = create_engine(postgres_dsn), то ошибка
        #  sqlalchemy.exc.ArgumentError: Expected string or URL object,
        #  got MultiHostUrl('postgresql://postgres:6051@localhost/postgres')
        session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.base.metadata.create_all(bind=engine)
        return session_local


class Base(DeclarativeBase):
    pass


DB_INITIALIZER = DatabaseInitializer(Base())

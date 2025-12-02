from sqlalchemy.orm import Session

from config.database.session import get_db_session
from ieinfo.application.port.ie_info_repository_port import IEInfoRepositoryPort


class IEInfoRepositoryImpl(IEInfoRepositoryPort):
    __instance = None


    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        if not hasattr(self, 'db'):
            self.db: Session = get_db_session()
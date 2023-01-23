from api.database_manager import DatabaseManager


class Model:

    @classmethod
    @property
    def objects(cls) -> DatabaseManager:
        return DatabaseManager(str(cls.__name__).lower())

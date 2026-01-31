from pymongo import MongoClient
from bot import LOGGER

class DataBaseHandle:
    _client = None
    _db = None

    def __init__(self, dburl: str = None) -> None:
        self._dburl = dburl
        if not DataBaseHandle._client:
            LOGGER.debug("Established MongoDB Connection")
            DataBaseHandle._client = MongoClient(self._dburl)
            DataBaseHandle._db = DataBaseHandle._client.get_database()
        self._db = DataBaseHandle._db

    def __del__(self):
        pass

import json
from datetime import datetime
from .mongo_db import DataBaseHandle
from bot import Config

class TidalSettings(DataBaseHandle):
    def __init__(self, dburl=None):
        if dburl is None:
            dburl = Config.DATABASE_URL
        super().__init__(dburl)
        self.collection = self._db.tidal_settings

    def set_variable(self, var_name, var_value, update_blob=False, blob_val=None):
        vtype = "str"
        if isinstance(var_value, bool):
            vtype = "bool"
        elif isinstance(var_value, int):
            vtype = "int"
        if update_blob:
            vtype = "blob"
            var_value = blob_val

        self.collection.update_one(
            {"var_name": var_name},
            {"$set": {
                "var_value": var_value,
                "vtype": vtype,
                "date_changed": datetime.now()
            }},
            upsert=True
        )

    def get_variable(self, var_name):
        doc = self.collection.find_one({"var_name": var_name})
        if doc:
            vtype = doc.get("vtype")
            val = doc.get("var_value")
            if vtype == "int":
                val = int(val)
            elif vtype == "bool":
                val = bool(val)
            return val, doc.get("blob_val")
        return None, None

class AuthedUsers(DataBaseHandle):
    def __init__(self, dburl=None):
        if dburl is None:
            dburl = Config.DATABASE_URL
        super().__init__(dburl)
        self.collection = self._db.authed_users

    def set_users(self, var_value):
        if not self.collection.find_one({"uid": var_value}):
            self.collection.insert_one({"uid": var_value})

    def get_users(self):
        docs = list(self.collection.find())
        return [(doc["uid"],) for doc in docs] if docs else [None]

class AuthedAdmins(DataBaseHandle):
    def __init__(self, dburl=None):
        if dburl is None:
            dburl = Config.DATABASE_URL
        super().__init__(dburl)
        self.collection = self._db.authed_admins

    def set_admins(self, var_value):
        if not self.collection.find_one({"uid": var_value}):
            self.collection.insert_one({"uid": var_value})

    def get_admins(self):
        docs = list(self.collection.find())
        return [(doc["uid"],) for doc in docs] if docs else [None]

class AuthedChats(DataBaseHandle):
    def __init__(self, dburl=None):
        if dburl is None:
            dburl = Config.DATABASE_URL
        super().__init__(dburl)
        self.collection = self._db.authed_chats

    def set_chats(self, var_value):
        if not self.collection.find_one({"uid": var_value}):
            self.collection.insert_one({"uid": var_value})

    def get_chats(self):
        docs = list(self.collection.find())
        return [(doc["uid"],) for doc in docs] if docs else [None]

class MusicDB(DataBaseHandle):
    def __init__(self, dburl=None):
        if dburl is None:
            dburl = Config.DATABASE_URL
        super().__init__(dburl)
        self.collection = self._db.music_table
        try:
            self.collection.create_index("msg_id", unique=True)
        except:
            pass

    def set_music(self, msg_id, title, artist, track_id, type):
        try:
            self.collection.insert_one({
                "msg_id": msg_id,
                "title": title,
                "artist": artist,
                "track_id": track_id,
                "type": type
            })
        except:
            pass

    def get_music_id(self, title, artist, track_id, type):
        docs = list(self.collection.find({"title": title}))
        for doc in docs:
            if doc.get("artist") == artist:
                if track_id:
                    try:
                        if doc.get("track_id") == int(track_id):
                            return doc["msg_id"], doc["artist"]
                    except:
                        pass
                if doc.get("type") == type:
                    return doc["msg_id"], doc["artist"]
        return None, None

class UserSettings(DataBaseHandle):
    shared_users = {}

    def __init__(self, dburl=None):
        if dburl is None:
            dburl = Config.DATABASE_URL
        super().__init__(dburl)
        self.collection = self._db.user_settings

    def set_var(self, user_id, var_name, var_value):
        user_id = str(user_id)
        
        if user_id in self.shared_users:
            self.shared_users[user_id][var_name] = var_value
        else:
            doc = self.collection.find_one({"user_id": user_id})
            if doc:
                jdata = json.loads(doc["json_data"])
                jdata[var_name] = var_value
                self.shared_users[user_id] = jdata
            else:
                self.shared_users[user_id] = {var_name: var_value}

        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"json_data": json.dumps(self.shared_users[user_id])}},
            upsert=True
        )

    def get_var(self, user_id, var_name):
        user_id = str(user_id)
        
        if user_id in self.shared_users:
            return self.shared_users[user_id].get(var_name)
        
        doc = self.collection.find_one({"user_id": user_id})
        if doc:
            jdata = json.loads(doc["json_data"])
            self.shared_users[user_id] = jdata
            return jdata.get(var_name)
        return None

class BroadcastUsers(DataBaseHandle):
    def __init__(self, dburl=None):
        if dburl is None:
            dburl = Config.DATABASE_URL
        super().__init__(dburl)
        self.collection = self._db.broadcast_users

    def add_user(self, user_id):
        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True
        )

    def get_all_users(self):
        return self.collection.find()

    def total_users_count(self):
        return self.collection.count_documents({})

set_db = TidalSettings()
users_db = AuthedUsers()
admins_db = AuthedAdmins()
chats_db = AuthedChats()
music_db = MusicDB()
user_settings = UserSettings()
broadcast_db = BroadcastUsers()

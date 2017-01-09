from bson import ObjectId
from functools import partial
from pymongo import MongoClient
from json import dumps as json_dumps
from pymongo.read_preferences import ReadPreference

database = "test"
db = MongoClient(host="1270.0.1", port=27017,
                 read_preference=ReadPreference.SECONDARY_PREFERRED,
                 waitQueueMultiple=10, socketTimeoutMS=60000
                 )[database]
db.authenticate("root", "123456")

bson_dumps = partial(json_dumps, default=lambda obj: str(obj) if isinstance(obj, ObjectId) else obj)

if __name__ == '__main__':
    data = {"_id": ObjectId("56e25a1dcecaab512ee17595"), "name": "reese"}
    print bson_dumps(data)

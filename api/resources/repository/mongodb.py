import pymongo
from common.constants import *

mongo_client = pymongo.MongoClient(MONGODB_URI)

mongo_db = mongo_client[MONGODB_DATABASE]

schedule_collection = mongo_db[SCHEDULE_COLLECTION]
schedule_collection.create_index(
    [("createdDate", 1)], expireAfterSeconds=MONGODB_DOCUMENT_EXPIRE_TIME)

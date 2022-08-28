from common.constants import *
from resources.repository.mongodb import *
from bson.objectid import ObjectId


def getTimetableStatus(id):
    time_table = schedule_collection.find_one({"_id": ObjectId(id)})
    if not time_table:
        raise ValueError("Cannot find document with id: {}".format(id))
    return {"status":time_table["status"]}


def getTimeTableData(id):
    time_table = schedule_collection.find_one({"_id": ObjectId(id)})
    if not time_table:
        raise ValueError("Cannot find document with id: {}".format(id))

    if not time_table["status"] or time_table["status"] != SCHEDULE_STATUS["FINISHED"]:
        raise ValueError("Process has not finished yet")

    if not time_table["data"]:
        raise ValueError("No data in document")

    return time_table["data"]

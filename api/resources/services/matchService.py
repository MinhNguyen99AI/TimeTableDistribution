from common.util import readDataframeFrombase64, zipExporters
from common.constants import *

import pandas as pd
from tqdm import tqdm
import datetime

from resources.repository.mongodb import *
from bson.objectid import ObjectId

from resources.services.exporter.schoolDetailExporter import SchoolDetailExporter
from resources.services.exporter.teacherDetailExporter import TeacherDetailExporter
from resources.services.exporter.teacherMasterExporter import TeacherMasterExporter

from threading import Thread

from resources.services.matchServiceHelper import run


def job(df_truong, df_GVNN, df_GVVN, id):
    # gvnn_result, gvvn_result = run(df_truong, df_GVNN, df_GVVN, id)

    # df_all_result = pd.concat([gvnn_result, gvvn_result]).reset_index()

    df_all_result = pd.read_excel("D:/[RESULTS] END RESULT.xlsx")

    school_detail = SchoolDetailExporter(
        df_all_result, "TKB chi tiết trường.xlsx")

    gvnn_detail = TeacherDetailExporter(
        df_all_result, "TKB GVNN - chi tiết.xlsx", TYPE_GVNN)
    gvnn_master = TeacherMasterExporter(
        df_all_result, "TKB GVNN - tổng.xlsx", TYPE_GVNN)

    gvvn_detail = TeacherDetailExporter(
        df_all_result, "TKB GVVN - chi tiết.xlsx", TYPE_GVVN)
    gvvn_master = TeacherMasterExporter(
        df_all_result, "TKB GVVN - tổng.xlsx", TYPE_GVVN)

    result_bytes = zipExporters(
        [school_detail, gvnn_detail, gvnn_master, gvvn_detail, gvvn_master])

    schedule_collection.find_one_and_update({"_id": ObjectId(
        id)}, {'$set': {"status": SCHEDULE_STATUS["FINISHED"], "data": result_bytes}})


def match(school_data, teacher_domestic_data, teacher_foreign_data) -> bytes:
    tqdm.pandas()
    df_truong, df_GVNN, df_GVVN = None, None, None
    # df_truong = readDataframeFrombase64(school_data['data'])
    # df_GVVN = readDataframeFrombase64(
    #     teacher_domestic_data['data'])
    # df_GVNN = readDataframeFrombase64(teacher_foreign_data['data'])

    result = schedule_collection.insert_one(
        {"status": SCHEDULE_STATUS["PENDING"], "createdDate": datetime.datetime.utcnow()})

    id = str(result.inserted_id)

    # Start async job
    # thread = Thread(target=job, args=(df_truong, df_GVNN, df_GVVN, id))
    # thread.start()

    job(df_truong, df_GVNN, df_GVVN, id)

    return {"id": id}

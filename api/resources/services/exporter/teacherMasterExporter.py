import pandas as pd
from common.util import getClassName
from common.constants import *


class TeacherMasterExporter:
    def __init__(self, df, name, type):
        self.df = df.copy(deep=True)
        self.name = name
        self.type = type
        self.preprocess_df()

    def preprocess_df(self):
        self.df['Buổi'] = self.df.apply(
            lambda row: "Sáng" if row['Tiet_Trong_Ngay'] < 5 else "Chiều", axis=1)
        self.df['Lớp'] = self.df.apply(getClassName, axis=1)

    def getName(self):
        return self.name

    def process(self, buffer):
        gv_master_dict = []

        if self.type == TYPE_GVNN:
            # GVNN
            teachers = self.df["Ten Giao Vien Nuoc Ngoai"].unique()
        else:
            # GVVN
            teachers = pd.unique(self.df[['Ten Giao Vien Viet Nam',
                                          'Ten Giao Vien Tro Giang']].values.ravel('K'))

        for teacher in teachers:
            if teacher == LACK_TEACHER_NAME or teacher == NO_TEACHER_NAME:
                continue
            sessions = []

            for session in ["Sáng", "Chiều"]:
                d = {
                    "Tên": teacher,
                    "Buổi": session
                }
                class_per_session = 0

                for day in range(2, 7 + 1):
                    if self.type == TYPE_GVNN:
                        sub_df = self.df[(self.df["Ten Giao Vien Nuoc Ngoai"] == teacher) & (
                            self.df["Buổi"] == session) & (self.df["Thu"] == day)]
                    else:
                        sub_df = self.df[((self.df["Ten Giao Vien Viet Nam"] == teacher) | (self.df["Ten Giao Vien Tro Giang"] == teacher)) & (
                            self.df["Buổi"] == session) & (self.df["Thu"] == day)]

                    class_per_session += len(sub_df)
                    clazz = ""
                    if len(sub_df) > 0:
                        clazz = sub_df.iloc[0]["Ten Truong"] + \
                            ": " + sub_df['Lớp'].str.cat(sep=', ')

                    day_detail = {"Lớp": clazz, "Ps": len(sub_df)}
                    d["Thứ " + str(day)] = day_detail
                d["Tiết/Buổi"] = class_per_session
                sessions.append(d)

            total_class = 0

            for d in sessions:
                total_class += d.get("Tiết/Buổi", 0)

            for d in sessions:
                d["Tổng tiết"] = total_class
                d["Tổng giờ"] = total_class * 2/3

            gv_master_dict += sessions

        df_gv_master = pd.json_normalize(gv_master_dict)
        df_gv_master.to_excel("D:/out.xlsx")
        df_gv_master = df_gv_master.set_index(['Tên', "Buổi"])
        df_gv_master.columns = df_gv_master.columns.str.split(".").map(
            lambda x: x if len(x) == 2 else x + [""]*(2-len(x))).map(tuple)
        dfs = {"gnvv-master": df_gv_master}
        self.writeToFile(buffer, dfs)

    def writeToFile(self, buffer, dfs):
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
        for sheetname, df in dfs.items():  # loop through `dict` of dataframes
            df.to_excel(writer, sheet_name=sheetname)  # send df to writer
            worksheet = writer.sheets[sheetname]  # pull worksheet object

            worksheet.set_column(0, 0, 20)  # set column width Tên
            worksheet.set_column(1, 1, 20)  # set column width Buổi

            worksheet.merge_range("C3:N3", None)
            # merge tổng tiết + tổng giờ
            for i in range(len(df.index)):
                worksheet.merge_range(3 + i*2, 3, 3 + i*2 + 1, 3, None)
                worksheet.merge_range(3 + i*2, 4, 3 + i*2 + 1, 4, None)

            for idx, col in enumerate(df, 2):  # loop through all columns
                col_len = 10
                if "Lớp" in col:
                    col_len = 30
                if "Ps" in col:
                    col_len = 4
                worksheet.set_column(idx, idx, col_len)  # set column width
        writer.save()

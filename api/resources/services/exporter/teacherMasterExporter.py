import pandas as pd
from common.util import is_one_val


class TeacherMasterExporter:
    def __init__(self, df, name):
        self.df = df
        self.name = name
        self.preprocess_df()

    def preprocess_df(self):
        self.df['Buổi'] = self.df.apply(
            lambda row: "Sáng" if row['Tiet_Trong_Ngay'] < 5 else "Chiều", axis=1)
        self.df['Lớp'] = self.df.apply(lambda row: str(
            int(row['Khoi'])) + 'A' + str(int(row['Lop so'])), axis=1)

    def getName(self):
        return self.name

    def process(self, buffer):
        gv_master_dict = []

        for name in self.df["Ten Giao Vien Duoc Xep"].unique():
            if name == "THIEU GIAO VIEN":
                continue
            sessions = []

            for session in ["Sáng", "Chiều"]:
                d = {"Tên": name, "Buổi": session}
                class_per_session = 0

                for day in range(2, 6 + 1):
                    sub_df = self.df[(self.df["Ten Giao Vien Duoc Xep"] == name) & (
                        self.df["Buổi"] == session) & (self.df["Thu"] == day)]
                    if not is_one_val(sub_df["Ten Truong"]):
                        raise ValueError(
                            "Giáo viên {} dạy nhiều trường trong buổi {} thứ {}".format(name, session, day))

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

            gv_master_dict += sessions

        df_gv_master = pd.json_normalize(gv_master_dict)
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

            for idx, col in enumerate(df, 2):  # loop through all columns
                col_len = 10
                if "Lớp" in col:
                    col_len = 30
                if "Ps" in col:
                    col_len = 4
                worksheet.set_column(idx, idx, col_len)  # set column width
        writer.save()

import pandas as pd
from operator import add


class TeacherDetailExporter:
    def __init__(self, df, name):
        self.df = df
        self.name = name
        self.vi_session = {"Morning": "Sáng", "Afternoon": "Chiều"}

        self.preprocess_df()

    def preprocess_df(self):
        self.df['Buổi'] = self.df.apply(
            lambda row: "Sáng" if row['Tiet_Trong_Ngay'] < 5 else "Chiều", axis=1)
        self.df['Lớp'] = self.df.apply(lambda row: str(
            int(row['Khoi'])) + 'A' + str(int(row['Lop so'])), axis=1)
        self.df['Document'] = self.df.apply(
            lambda row: "Tieng Anh " + str(int(row['Khoi'])), axis=1)
        self.df["Tiet trong buoi"] = self.df.apply(
            lambda row: int(row['Tiet_Trong_Ngay'] % 4 + 1), axis=1)

    def getName(self):
        return self.name

    def process(self, buffer):
        dfs = {}

        for teacher in self.df["Ten Giao Vien Duoc Xep"].unique():
            gv_detail_dict = []

            if teacher == "THIEU GIAO VIEN":
                continue

            metadata = {"Periods Count": [0, 0, 0, 0, 0]}
            df_detail_list = []
            for session in ["Morning", "Afternoon"]:
                df_detail_list.append(
                    self.getTeacherDetailRowsbySession(teacher, session))
                metadata["School " +
                         session] = self.getTeacherSchool(teacher, session)
                metadata["Periods Count"] = list(
                    map(add, metadata["Periods Count"], self.countClassInSession(df_detail_list[-1])))

            dfs[teacher] = (*df_detail_list, metadata)

        self.writeToFileTeacherDetail(buffer, dfs)

    def getTeacherSchool(self, teacher, session):
        sub_df = self.df[(self.df["Ten Giao Vien Duoc Xep"] == teacher) & (
            self.df["Buổi"] == self.vi_session[session])].groupby("Thu").first()["Ten Truong"]
        school = [None] * 5
        for day, row in zip(sub_df.index.tolist(), sub_df):
            school[int(day) - 2] = row
        return school

    def initTeacherDetailRowDict(self, session, period):
        d = {
            "Sessions": session,
            "Periods": period
        }

        for day in range(2, 7):
            d[self.getDayFromNum(day)] = {
                "Start time": None,
                "Class": None,
                "Document": None
            }
        return d

    def getTeacherDetailRowsbySession(self, teacher, session):
        gv_detail_dict = []
        for period in range(1, 4 + 1):
            d = self.initTeacherDetailRowDict(session, period)
            sub_df = self.df[(self.df["Ten Giao Vien Duoc Xep"] == teacher) & (
                self.df["Buổi"] == self.vi_session[session]) & (self.df["Tiet trong buoi"] == period)]

            for idx, row in sub_df.iterrows():
                d[self.getDayFromNum(row['Thu'])] = {
                    "Start time": None, 'Class': row['Lớp'], 'Document': row['Document']}
            gv_detail_dict.append(d)
        df_gv_detail = pd.json_normalize(gv_detail_dict)
        df_gv_detail = df_gv_detail.set_index(["Sessions", 'Periods'])
        df_gv_detail.columns = df_gv_detail.columns.str.split(".").map(tuple)
        return df_gv_detail

    def getDayFromNum(self, dayNum):
        if dayNum == 2:
            return "Monday"

        if dayNum == 3:
            return "Tuesday"

        if dayNum == 4:
            return "Wednesday"

        if dayNum == 5:
            return "Thursday"

        if dayNum == 6:
            return "Friday"

        if dayNum == 7:
            return "Saturday"
        return "Sunday"

    def initTeacherDetailRowDict(self, session, period):
        d = {
            "Sessions": session,
            "Periods": period
        }

        for day in range(2, 7):
            d[self.getDayFromNum(day)] = {
                "Start time": None,
                "Class": None,
                "Document": None
            }
        return d

    def writeToFileTeacherDetail(self, buffer, dfs):
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')

        for sheetname, (df_morning, df_afternoon, metadata) in dfs.items():
            # Write Morning data
            df_morning.to_excel(writer, sheet_name=sheetname)
            last_row = len(df_morning) + 3  # 3 for headers
            # Format columns length
            worksheet = writer.sheets[sheetname]
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, 10)

            for idx, col in enumerate(df_morning, 2):
                col_len = 10
                if "Class" in col:
                    col_len = 5
                if "Document" in col:
                    col_len = 12
                worksheet.set_column(idx, idx, col_len)

            self.addSchoolName(metadata['School Morning'],
                               worksheet, last_row, writer.book)
            last_row += 1

            # Write Afternoon data
            df_afternoon.to_excel(
                writer, sheet_name=sheetname, header=None, startrow=last_row)
            last_row += len(df_afternoon) + 1

            self.addSchoolName(metadata['School Afternoon'],
                               worksheet, last_row, writer.book)
            last_row += 1

            # Write period counts
            self.writePeriodCount(metadata["Periods Count"],
                                  worksheet, last_row, writer.book)
        writer.save()

    def addSchoolName(self, schools, worksheet, startrow, workbook):
        school_style = workbook.add_format(
            {
                'bold': True,
                'border': True,
                'align': 'center'
            })
        worksheet.write(startrow, 0, "SCHOOL", school_style)
        worksheet.merge_range(startrow, 0, startrow, 1, None)

        for idx, data in enumerate(schools):
            column_idx = 2 + idx * 3
            worksheet.write(startrow, column_idx, data, school_style)
            worksheet.merge_range(startrow, column_idx,
                                  startrow, column_idx + 2, None)

    def writePeriodCount(self, periods, worksheet, startrow, workbook):
        period_style = workbook.add_format(
            {
                'bold': True,
                'border': True,
                'align': 'center'
            })
        worksheet.write(startrow, 0, "TOTAL periods", period_style)
        worksheet.merge_range(startrow, 0, startrow, 1, None)

        for idx, data in enumerate(periods):
            column_idx = 2 + idx * 3
            worksheet.write(startrow, column_idx, data, period_style)
            worksheet.merge_range(startrow, column_idx,
                                  startrow, column_idx + 2, None)

        worksheet.write(startrow, len(periods)*3 + 2,
                        sum(periods), period_style)

    def countClassInSession(self, df):
        classCountByDay = []
        for day in range(2, 6 + 1):
            classCountByDay.append(
                df[self.getDayFromNum(day)]["Class"].notnull().sum())

        return classCountByDay

import pandas as pd
from operator import add
from common.util import getDayFromNum, getClassName


class TeacherDetailExporter:
    def __init__(self, df, name):
        self.df = df.copy(deep=True)
        self.name = name
        self.vi_session = {"Morning": "Sáng", "Afternoon": "Chiều"}

        self.preprocess_df()

    def preprocess_df(self):
        self.df['Buổi'] = self.df.apply(
            lambda row: "Sáng" if row['Tiet_Trong_Ngay'] < 5 else "Chiều", axis=1)
        self.df['Lớp'] = self.df.apply(getClassName, axis=1)
        self.df['Document'] = self.df.apply(
            lambda row: row["Document"], axis=1)
        self.df["Tiet trong buoi"] = self.df.apply(
            lambda row: int(row['Tiet_Trong_Ngay'] % 4 + 1), axis=1)

    def getName(self):
        return self.name

    def process(self, buffer):
        dfs = {}

        for teacher in self.df["Ten Giao Vien Duoc Xep"].unique():
            if teacher == "THIEU GIAO VIEN":
                continue

            metadata = {"Periods Count": [0, 0, 0, 0, 0]}
            df_detail_list = []
            for session in ["Morning", "Afternoon"]:
                dict_detail = self.getTeacherDetailRowsbySession(
                    teacher, session)
                df_detail_list.append(dict_detail)
                metadata["School " +
                         session] = self.getTeacherSchool(teacher, session)
                metadata["Periods Count"] = list(
                    map(add, metadata["Periods Count"], self.countClassInSession(dict_detail)))

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
            d[getDayFromNum(day)] = {
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

            for _, row in sub_df.iterrows():
                d[getDayFromNum(row['Thu'])] = {
                    "Start time": None, 'Class': row['Lớp'], 'Document': row['Document']}
            gv_detail_dict.append(d)
        return gv_detail_dict

    def writeDayRow(self, worksheet, row, col, day):
        worksheet.write(row, col, day, self.header_style)
        worksheet.merge_range(row, col, row, col + 2, None)

        worksheet.write(row + 1, col, "Start time", self.header_style)
        worksheet.write(row + 1, col + 1, "Class", self.header_style)
        worksheet.write(row + 1, col + 2, "Document", self.header_style)

    def add_headers(self, worksheet):
        worksheet.write('A3', "Sessions", self.header_style)
        worksheet.write('B3', "Periods", self.header_style)
        worksheet.write('A4', "Morning", self.header_style)
        worksheet.merge_range('A4:A7', None)
        for i in range(1, 5):
            worksheet.write(i+2, 1, i, self.header_style)

        worksheet.write('A8', "School", self.header_style)
        worksheet.merge_range('A8:B8', None)

        worksheet.write('A9', "Sessions", self.header_style)
        worksheet.write('B9', "Periods", self.header_style)
        worksheet.write('A10', "Afternoon", self.header_style)
        worksheet.merge_range('A10:A13', None)
        for i in range(1, 5):
            worksheet.write(i+8, 1, i, self.header_style)

        worksheet.write('A14', "School", self.header_style)
        worksheet.merge_range('A14:B14', None)

        worksheet.write('A15', "Total periods", self.header_style)
        worksheet.merge_range('A15:B15', None)

        worksheet.merge_range('C3:Q3', None)

        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 10)

        # Day headers
        self.writeDayRow(worksheet, 0, 2, "Monday")
        self.writeDayRow(worksheet, 0, 5, "Tuesday")
        self.writeDayRow(worksheet, 0, 8, "Wednesday")
        self.writeDayRow(worksheet, 0, 11, "Thursday")
        self.writeDayRow(worksheet, 0, 14, "Friday")

    def writeSessionData(self, worksheet, df, start_row):
        for row in df:
            for idx, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]):
                info = row[day]
                current_row = start_row + row["Periods"]
                current_col = 2 + idx * 3

                worksheet.write(current_row, current_col,
                                info["Start time"], self.cell_style)
                worksheet.write(current_row, current_col + 1,
                                info["Class"], self.cell_style)
                worksheet.write(current_row, current_col + 2,
                                info["Document"], self.cell_style)

                worksheet.set_column(current_col, current_col, 10)
                worksheet.set_column(current_col + 1, current_col + 1, 5)
                worksheet.set_column(current_col + 2, current_col + 2, 12)

    def writeToFileTeacherDetail(self, buffer, dfs):
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
        workbook = writer.book

        self.header_style = workbook.add_format(
            {
                'bold': True,
                'border': True,
                'align': 'center'
            })

        self.cell_style = workbook.add_format(
            {
                'border': True,
                'align': 'center'
            })

        for sheetname, (df_morning, df_afternoon, metadata) in dfs.items():
            worksheet = workbook.add_worksheet(sheetname)

            for r in range(15):
                for c in range(17):
                    worksheet.write_blank(r, c, '', self.cell_style)

            self.add_headers(worksheet)

            self.writeSessionData(worksheet, df_morning, 2)
            self.writeSessionData(worksheet, df_afternoon, 9)

            self.addSchoolName(metadata['School Morning'], worksheet, 7)
            self.addSchoolName(metadata['School Afternoon'], worksheet, 13)

            self.writePeriodCount(metadata["Periods Count"],
                                  worksheet, 14)

        writer.save()

    def addSchoolName(self, schools, worksheet, startrow):
        for idx, data in enumerate(schools):
            column_idx = 2 + idx * 3
            worksheet.write(startrow, column_idx, data, self.header_style)
            worksheet.merge_range(startrow, column_idx,
                                  startrow, column_idx + 2, None)

    def writePeriodCount(self, periods, worksheet, startrow):
        for idx, data in enumerate(periods):
            column_idx = 2 + idx * 3
            worksheet.write(startrow, column_idx, data, self.header_style)
            worksheet.merge_range(startrow, column_idx,
                                  startrow, column_idx + 2, None)

        worksheet.write(startrow, len(periods)*3 + 2,
                        sum(periods), self.header_style)

    def countClassInSession(self, d):
        df = pd.json_normalize(d)
        df = df.set_index(["Sessions", 'Periods'])
        df.columns = df.columns.str.split(".").map(tuple)

        classCountByDay = []
        for day in range(2, 6 + 1):
            classCountByDay.append(
                df[getDayFromNum(day)]["Class"].notnull().sum())

        return classCountByDay

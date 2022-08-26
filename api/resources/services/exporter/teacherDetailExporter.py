import pandas as pd
from operator import add
from common.util import getDayFromNum, getClassName
from common.constants import *


class TeacherDetailExporter:
    def __init__(self, df, name, type):
        self.df = df.copy(deep=True)
        self.name = name
        self.vi_session = {"Morning": "Sáng", "Afternoon": "Chiều"}
        self.type = type

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
        if self.type == TYPE_GVNN:
            sub_df = self.df[(self.df["Ten Giao Vien Nuoc Ngoai"] == teacher) & (
                self.df["Buổi"] == self.vi_session[session])].groupby("Thu").first()["Ten Truong"]
        else:
            sub_df = self.df[((self.df["Ten Giao Vien Viet Nam"] == teacher) | (self.df["Ten Giao Vien Tro Giang"] == teacher)) & (
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
                "Document": None,
                "Is TA": None,
                "TA": None,
                "TA Tel": None
            }
        return d

    def getTANameAndStatus(self, teacher, row):
        is_TA = False
        TA = None
        if self.type == TYPE_GVNN:
            if row["Ten Giao Vien Viet Nam"] != NO_TEACHER_NAME:
                TA = row["Ten Giao Vien Viet Nam"]
        else:
            # GVVN
            if row["Ten Giao Vien Viet Nam"] == teacher:
                if row["Ten Giao Vien Nuoc Ngoai"] == NO_TEACHER_NAME:
                    is_TA = False
                    if row["Ten Giao Vien Tro Giang"] != NO_TEACHER_NAME:
                        TA = row["Ten Giao Vien Tro Giang"]
                else:
                    is_TA = True
            else:
                is_TA = True

        return is_TA, TA

    def getTeacherDetailRowsbySession(self, teacher, session):
        gv_detail_dict = []
        for period in range(1, 4 + 1):
            d = self.initTeacherDetailRowDict(session, period)
            if self.type == TYPE_GVNN:
                sub_df = self.df[(self.df["Ten Giao Vien Nuoc Ngoai"] == teacher) & (
                    self.df["Buổi"] == self.vi_session[session]) & (self.df["Tiet trong buoi"] == period)]
            else:
                sub_df = self.df[((self.df["Ten Giao Vien Viet Nam"] == teacher) | (self.df["Ten Giao Vien Tro Giang"] == teacher)) & (
                    self.df["Buổi"] == self.vi_session[session]) & (self.df["Tiet trong buoi"] == period)]

            for _, row in sub_df.iterrows():
                is_TA, TA = self.getTANameAndStatus(teacher, row)
                d[getDayFromNum(row['Thu'])] = {"Start time": None, 'Class': row['Lớp'],
                                                'Document': row['Document'], "Is TA": is_TA, 'TA': TA, 'TA Tel': None}
            gv_detail_dict.append(d)
        return gv_detail_dict

    def writeDayRow(self, worksheet, row, col, day):
        worksheet.write(row, col, day, self.header_style)
        worksheet.merge_range(row, col, row, col + 4, None)

        worksheet.write(row + 1, col, "Start time", self.header_style)
        worksheet.write(row + 1, col + 1, "Class", self.header_style)
        worksheet.write(row + 1, col + 2, "Document", self.header_style)
        worksheet.write(row + 1, col + 3, "TA", self.header_style)
        worksheet.write(row + 1, col + 4, "Tel", self.header_style)

    def add_headers(self, worksheet):
        worksheet.write('A1', "Sessions", self.header_style)
        worksheet.merge_range('A1:A2', None)
        worksheet.write('B1', "Periods", self.header_style)
        worksheet.merge_range('B1:B2', None)
        worksheet.write('A3', "School", self.header_style)
        worksheet.merge_range('A3:B3', None)
        worksheet.write('A4', "Address", self.header_style)
        worksheet.merge_range('A4:B4', None)

        worksheet.write('A5', "Morning", self.header_style)
        worksheet.merge_range('A5:A9', None)
        for i in range(1, 6):
            worksheet.write(i+3, 1, i, self.header_style)

        worksheet.write('A10', "School", self.header_style)
        worksheet.merge_range('A10:B10', None)
        worksheet.write('A11', "Address", self.header_style)
        worksheet.merge_range('A11:B11', None)

        worksheet.write('A12', "Afternoon", self.header_style)
        worksheet.merge_range('A12:A15', None)
        for i in range(1, 5):
            worksheet.write(i+10, 1, i, self.header_style)

        worksheet.write('A16', "Total periods", self.header_style)
        worksheet.merge_range('A16:B16', None)

        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 10)

        # Day headers
        self.writeDayRow(worksheet, 0, 2, "Monday")
        self.writeDayRow(worksheet, 0, 7, "Tuesday")
        self.writeDayRow(worksheet, 0, 12, "Wednesday")
        self.writeDayRow(worksheet, 0, 17, "Thursday")
        self.writeDayRow(worksheet, 0, 22, "Friday")

    def writeSessionData(self, worksheet, df, start_row):
        for row in df:
            for idx, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]):
                info = row[day]
                current_row = start_row + row["Periods"]
                current_col = 2 + idx * 5

                worksheet.write(current_row, current_col,
                                info["Start time"], self.cell_style)
                worksheet.write(current_row, current_col + 1,
                                info["Class"], self.cell_style)
                worksheet.write(current_row, current_col + 2,
                                info["Document"], self.cell_style)
                worksheet.write(current_row, current_col + 3,
                                info["TA"], self.cell_style)
                worksheet.write(current_row, current_col + 4,
                                info["TA Tel"], self.cell_style)

                worksheet.set_column(current_col, current_col, 10)
                worksheet.set_column(current_col + 1, current_col + 1, 5)
                worksheet.set_column(current_col + 2, current_col + 2, 12)
                worksheet.set_column(current_col + 3, current_col + 3, 25)
                worksheet.set_column(current_col + 4, current_col + 4, 15)

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

            for r in range(16):
                for c in range(27):
                    worksheet.write_blank(r, c, '', self.cell_style)

            self.add_headers(worksheet)

            self.writeSessionData(worksheet, df_morning, 3)
            self.writeSessionData(worksheet, df_afternoon, 10)

            self.addSchoolName(metadata['School Morning'], worksheet, 2)
            self.addSchoolName(metadata['School Afternoon'], worksheet, 9)

            self.writePeriodCount(metadata["Periods Count"],
                                  worksheet, 15)

        writer.save()

    def addSchoolName(self, schools, worksheet, startrow):
        for idx, data in enumerate(schools):
            column_idx = 2 + idx * 5
            # School data
            worksheet.write(startrow, column_idx, data, self.header_style)
            worksheet.merge_range(startrow, column_idx,
                                  startrow, column_idx + 4, None)
            # School address data
            worksheet.merge_range(startrow + 1, column_idx,
                                  startrow + 1, column_idx + 4, None)

    def writePeriodCount(self, periods, worksheet, startrow):
        for idx, data in enumerate(periods):
            column_idx = 2 + idx * 5
            worksheet.write(startrow, column_idx, data, self.header_style)
            worksheet.merge_range(startrow, column_idx,
                                  startrow, column_idx + 4, None)

        worksheet.write(startrow, len(periods)*5 + 2,
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

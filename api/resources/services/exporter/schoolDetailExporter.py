import pandas as pd
from common.util import getClassName, getTeacherName
from common.constants import *


class SchoolDetailExporter:
    def __init__(self, df, name):
        self.df = df.copy(deep=True)
        self.name = name
        self.styles = {}
        self.preprocess_df()

    def preprocess_df(self):
        self.df['Buổi'] = self.df.apply(
            lambda row: "Sáng" if row['Tiet_Trong_Ngay'] < 5 else "Chiều", axis=1)
        self.df['Lớp'] = self.df.apply(getClassName, axis=1)
        self.df["Tiet trong buoi"] = self.df.apply(
            lambda row: int(row['Tiet_Trong_Ngay'] % 4 + 1), axis=1)

    def getName(self):
        return self.name

    def getSchoolSchedule(self, school):
        sub_df = self.df[(self.df["Ten Truong"] == school)]
        school_schedule = {
            "2": {
                "Sáng": {},
                "Chiều": {}
            },
            "3": {
                "Sáng": {},
                "Chiều": {}
            },
            "4": {
                "Sáng": {},
                "Chiều": {}
            },
            "5": {
                "Sáng": {},
                "Chiều": {}
            },
            "6": {
                "Sáng": {},
                "Chiều": {}
            }
        }

        for _, row in sub_df.iterrows():
            current_session = school_schedule[str(
                int(row["Thu"]))][row["Buổi"]]

            current_classes = current_session.get(
                str(row["Tiet trong buoi"]), [])

            gvnn = getTeacherName(row["Ten Giao Vien Nuoc Ngoai"])
            gvvn = getTeacherName(row["Ten Giao Vien Viet Nam"])
            ta = getTeacherName(row["Ten Giao Vien Tro Giang"])

            if gvnn:
                ta = gvvn
                gvvn = None

            current_classes.append({
                "class": row["Lớp"],
                "GVNN": gvnn,
                "GVVN": gvvn,
                "TA": ta
            })

            current_session[str(row["Tiet trong buoi"])] = current_classes

        return school_schedule

    def add_headers(self, worksheet):
        worksheet.write('A1', "Buổi", self.styles["header"])
        worksheet.merge_range('A1:A2', None)
        worksheet.write('B1', "Tiết", self.styles["header"])
        worksheet.merge_range('B1:B2', None)

        worksheet.write('A3', "SÁNG", self.styles["header"])
        worksheet.merge_range('A3:A6', None)
        worksheet.write('A7', "CHIỀU", self.styles["header"])
        worksheet.merge_range('A7:A10', None)

        for i in range(1, 5):
            worksheet.write(1 + i, 1, i, self.styles["header"])
            worksheet.write(5 + i, 1, i, self.styles["header"])

    def process(self, buffer):
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')

        workbook = writer.book

        self.setCellsFormat(workbook)

        for school in self.df["Ten Truong"].unique().tolist():
            schedule = self.getSchoolSchedule(school)
            self.worksheet = workbook.add_worksheet(school[:30])

            self.add_headers(self.worksheet)

            current_col = 2
            for day in ['2', '3', '4', '5', '6']:
                self.worksheet.write(
                    0, current_col, "Thứ {}".format(day), self.styles["header"])

                col_width = max(1, self.findMaxConcurrentClassNum(schedule[day]["Sáng"]),
                                self.findMaxConcurrentClassNum(schedule[day]["Chiều"]))*4
                # Set Column size
                self.worksheet.set_column(
                    current_col, current_col + col_width - 1, 20)
                if col_width > 1:
                    self.worksheet.merge_range(
                        0, current_col, 0, current_col + col_width - 1, None)

                for session in ["Sáng", "Chiều"]:
                    self.writeSchedule(schedule, session, day,
                                       current_col, col_width)

                current_col += col_width

        writer.save()

    def findMaxConcurrentClassNum(self, period_data):
        result = 0
        for _, v in period_data.items():
            result = max(result, len(v))
        return result

    def writeSchedule(self, schedule, session, day, current_col, col_width):
        if session == "Sáng":
            start_row = 1
        else:
            start_row = 5

        for col in range(current_col + len(schedule[day][session]), current_col + col_width):
            self.worksheet.write_blank(
                start_row, col, '', self.styles["header"])
            for i in range(start_row + 1, start_row + 5):
                self.worksheet.write_blank(i, col, '', self.styles["cell"])

        if session == "Sáng":
            for col in range(col_width//4):
                self.worksheet.write(1, current_col + col*4,
                                     "Lớp", self.styles["header"])
                self.worksheet.write(
                    1, current_col + col*4 + 1, "GV Nước ngoài", self.styles["header"])
                self.worksheet.write(
                    1, current_col + col*4 + 2, "GV Việt Nam", self.styles["header"])
                self.worksheet.write(
                    1, current_col + col*4 + 3, "Trợ giảng", self.styles["header"])

        for k, period_data in schedule[day][session].items():
            period = int(k)
            for idx, cls in enumerate(period_data):
                self.worksheet.write(
                    start_row + period, current_col + idx*4, cls['class'], self.styles["cell_" + str(idx % 2)])
                self.worksheet.write(
                    start_row + period, current_col + idx*4 + 1, cls['GVNN'], self.styles["cell_" + str(idx % 2)])
                self.worksheet.write(
                    start_row + period, current_col + idx*4 + 2, cls['GVVN'], self.styles["cell_" + str(idx % 2)])
                self.worksheet.write(
                    start_row + period, current_col + idx*4 + 3, cls['TA'], self.styles["cell_" + str(idx % 2)])

    def setCellsFormat(self, workbook):
        self.styles["header"] = workbook.add_format(
            {
                'bold': True,
                'border': True,
                'align': 'center'
            })
        self.styles["cell"] = workbook.add_format(
            {
                'border': True,
                'align': 'center'
            })
        self.styles["cell_0"] = workbook.add_format(
            {
                'border': True,
                'align': 'center',
                'bg_color': 'B1D7B4'
            })
        self.styles["cell_1"] = workbook.add_format(
            {
                'border': True,
                'align': 'center',
                'bg_color': 'E6D2AA'
            })

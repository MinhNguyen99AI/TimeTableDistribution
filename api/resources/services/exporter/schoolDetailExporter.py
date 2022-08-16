import pandas as pd
from common.util import getClassName


class SchoolDetailExporter:
    def __init__(self, df, name):
        self.df = df.copy(deep=True)
        self.name = name
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
                row["Ten Giao Vien Duoc Xep"], [None, None, None, None])
            current_classes[row["Tiet trong buoi"] - 1] = row["Lớp"]

            current_session[row["Ten Giao Vien Duoc Xep"]] = current_classes

        return school_schedule

    def add_headers(self, worksheet):
        worksheet.write(2, 0, "SÁNG", self.header_style)
        worksheet.merge_range(2, 0, 5, 0, None)
        worksheet.write(7, 0, "CHIỀU", self.header_style)
        worksheet.merge_range(7, 0, 10, 0, None)
        worksheet.write(1, 1, "Giáo viên", self.header_style)
        worksheet.write(6, 1, "Giáo viên", self.header_style)

        worksheet.write(0, 0, "Buổi", self.header_style)
        worksheet.write(0, 1, "Tiết", self.header_style)

        for i in range(1, 5):
            worksheet.write(1 + i, 1, i, self.header_style)
            worksheet.write(6 + i, 1, i, self.header_style)

    def process(self, buffer):
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

        for school in self.df["Ten Truong"].unique().tolist():
            schedule = self.getSchoolSchedule(school)
            self.worksheet = workbook.add_worksheet(school[:30])

            self.add_headers(self.worksheet)

            current_col = 2
            for day in ['2', '3', '4', '5', '6']:
                self.worksheet.write(
                    0, current_col, "Thứ {}".format(day), self.header_style)
                col_width = max(1, len(schedule[day]["Sáng"]), len(
                    schedule[day]["Chiều"]))
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

    def writeSchedule(self, schedule, session, day, current_col, col_width):
        if session == "Sáng":
            header_row = 1
        else:
            header_row = 6

        for idx, (teacher, classes) in enumerate(schedule[day][session].items()):
            self.worksheet.write(header_row, current_col + idx,
                                 teacher, self.header_style)
            for period, cls in enumerate(classes):
                self.worksheet.write(
                    header_row + 1 + period, current_col + idx, cls, self.cell_style)

        for col in range(current_col + len(schedule[day][session]), current_col + col_width):
            self.worksheet.write_blank(header_row, col, '', self.header_style)
            for i in range(header_row + 1, header_row + 5):
                self.worksheet.write_blank(i, col, '', self.cell_style)

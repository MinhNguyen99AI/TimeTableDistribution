import pandas as pd


class SchoolDetailExporter:
    def __init__(self, df, name):

        self.df = df
        self.name = name

        self.df['Buổi'] = self.df.apply(
            lambda row: "Sáng" if row['Tiet_Trong_Ngay'] < 5 else "Chiều", axis=1)
        self.df['Lớp'] = self.df.apply(lambda row: str(
            int(row['Khoi'])) + 'A' + str(int(row['Lop so'])), axis=1)
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

    def process(self, buffer):
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')

        workbook = writer.book

        header_style = workbook.add_format(
            {
                'bold': True,
                'border': True,
                'align': 'center'
            })

        cell_style = workbook.add_format(
            {
                'border': True,
                'align': 'center'
            })

        for school in self.df["Ten Truong"].unique().tolist():
            schedule = self.getSchoolSchedule(school)
            worksheet = workbook.add_worksheet(school[:30])

            worksheet.write(2, 0, "SÁNG", header_style)
            worksheet.merge_range(2, 0, 5, 0, None)
            worksheet.write(7, 0, "CHIỀU", header_style)
            worksheet.merge_range(7, 0, 10, 0, None)
            worksheet.write(1, 1, "Giáo viên", header_style)
            worksheet.write(6, 1, "Giáo viên", header_style)

            worksheet.write(0, 0, "Buổi", header_style)
            worksheet.write(0, 1, "Tiết", header_style)

            for i in range(1, 5):
                worksheet.write(1 + i, 1, i, header_style)
                worksheet.write(6 + i, 1, i, header_style)

            current_col = 2
            for day in ['2', '3', '4', '5', '6']:
                worksheet.write(
                    0, current_col, "Thứ {}".format(day), header_style)
                col_width = max(1, len(schedule[day]["Sáng"]), len(
                    schedule[day]["Chiều"]))
                # Set Column size
                worksheet.set_column(
                    current_col, current_col + col_width - 1, 20)
                if col_width > 1:
                    worksheet.merge_range(
                        0, current_col, 0, current_col + col_width - 1, None)

                for idx, (teacher, classes) in enumerate(schedule[day]['Sáng'].items()):
                    worksheet.write(1, current_col + idx,
                                    teacher, header_style)
                    for period, cls in enumerate(classes):
                        worksheet.write(
                            2 + period, current_col + idx, cls, cell_style)

                for col in range(current_col + len(schedule[day]['Sáng']), current_col + col_width):
                    worksheet.write_blank(1, col, '', header_style)
                    for i in range(2, 6):
                        worksheet.write_blank(i, col, '', cell_style)

                for idx, (teacher, classes) in enumerate(schedule[day]['Chiều'].items()):
                    worksheet.write(6, current_col + idx,
                                    teacher, header_style)
                    for period, cls in enumerate(classes):
                        worksheet.write(
                            7 + period, current_col + idx, cls, cell_style)

                for col in range(current_col + len(schedule[day]['Chiều']), current_col + col_width):
                    worksheet.write_blank(6, col, '', header_style)
                    for i in range(7, 11):
                        worksheet.write_blank(i, col, '', cell_style)

                current_col += col_width

        writer.save()

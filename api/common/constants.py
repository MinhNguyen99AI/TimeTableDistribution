import os

EXCEL_FILE_EXTENSIONS = ['xls', 'xlsx']
NATIONALITY = {
    "native": ['Anh', 'Ai-len', 'Mỹ', 'Ai-Len', 'Nam Phi', 'Úc', 'Đan Mạch', 'Ailen', 'Ấn Độ', 'Hungari', 'Canada', 'Italy', 'Thuỵ Điển', 'Ý'],
    "non_native": ['Ai Cập', 'Thổ Nhĩ Kỳ', 'Pháp', 'Ukraine', 'Hy Lạp', 'Brasil', 'Morocco', 'Croatia', 'Russia', 'Ba Lan', 'Nga', 'Zimbabwean',  'Colombia']
}

SCHEDULE_STATUS = {
    "PENDING": "PENDING",
    "SCHOOL_COORDINATE_DONE": "SCHOOL_COORDINATE_DONE",
    "FOREIGN_COORDINATE_DONE": "FOREIGN_COORDINATE_DONE",
    "MATCHED_FOREIGN": "MATCHED_FOREIGN",
    "DOMESTIC_COORDINATE_DONE": "DOMESTIC_COORDINATE_DONE",
    "MATCHED_DOMESTIC": "MATCHED_DOMESTIC",
    "FINISHED": "FINISHED"
}

MONGODB_URL = os.environ['MONGODB_URL']
MONGODB_DATABASE = "timetable"
SCHEDULE_COLLECTION = "schoolSchedule"

MONGODB_DOCUMENT_EXPIRE_TIME = 172800  # 2 days

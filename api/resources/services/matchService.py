from common.util import readDataframeFrombase64, zipDataFrames


def match(school_data, teacher_data) -> bytes:
    df_school = readDataframeFrombase64(school_data['data'])
    df_teacher = readDataframeFrombase64(teacher_data['data'])

    print(df_school.head())
    print(df_teacher.head())
    return zipDataFrames([df_school, df_teacher], ["school.xlsx", "teacher.xlsx"])

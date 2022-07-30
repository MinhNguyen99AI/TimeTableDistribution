from common.util import readDataframeFrombase64


def match(school_data, teacher_data):
    df_school = readDataframeFrombase64(school_data['data'])
    df_teacher = readDataframeFrombase64(teacher_data['data'])

    print(df_school.head())
    print(df_teacher.head())
    return "test"

from common.util import readDataframeFrombase64, zipDataFrames
from resources.services.geocodingService import create_GV_DataFrame
import numpy as np


def match(school_data, teacher_data) -> bytes:
    df_school = readDataframeFrombase64(school_data['data'])
    df_teacher = readDataframeFrombase64(teacher_data['data'])

    df_school = create_Truong_DataFrame(df_school)
    df_teacher = create_GV_DataFrame(df_teacher)

    print(df_teacher.head())
    return zipDataFrames([df_school, df_teacher], ["school.xlsx", "teacher.xlsx"])


def create_Truong_DataFrame(df):
    df.index = df.iloc[:, 0]
    df = df.iloc[:, 1:]
    thu = [2, 4, 6, 3, 5]
    df['Thu'] = np.tile(thu, len(df)//len(thu) + 1)[:len(df)]
    newdf = df.sort_values(by=['Ten Truong', 'Thu'], axis=0, ascending=[False, True], inplace=False,
                           kind='quicksort', na_position='first', ignore_index=True, key=None)
    tietTrongNgay = [1, 2, 3, 4, 5, 6, 7, 8]
    newdf['Tiet_Trong_Ngay'] = np.tile(tietTrongNgay, len(
        newdf)//len(tietTrongNgay) + 1)[:len(newdf)]
    finaldf = newdf.sort_values(by=['Ten Truong', 'Khoi', 'Lop so'], axis=0, ascending=[False, True, True], inplace=False,
                                kind='quicksort', na_position='first', ignore_index=True, key=None)
    return finaldf

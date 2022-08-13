from common.util import readDataframeFrombase64, zipDataFrames
from common.constants import *

from resources.services.geocodingService import get_coordinates
import numpy as np
import pandas as pd
import math


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

    return newdf.sort_values(by=['Ten Truong', 'Khoi', 'Lop so'], axis=0, ascending=[False, True, True], inplace=False,
                             kind='quicksort', na_position='first', ignore_index=True, key=None)


def isTeacherNativeNation(nation: str) -> bool:
    if nation in NATIONALITY["native"]:
        return True

    if nation in NATIONALITY["non_native"]:
        return False

    return None


def rankTeacher(year_exp, native, is_new_teacher):
    if not isinstance(year_exp, str) and not math.isnan(year_exp, ):
        if int(year_exp) >= 2 and native and not is_new_teacher:
            return 'A'
        if int(year_exp) >= 1 and not is_new_teacher:
            return 'B'

    return 'C'


def create_GV_DataFrame(df):
    # create dataframe
    giao_vien_chi_tiet = pd.DataFrame(columns=[
                                      'Ten GV', 'Quoc Tich', 'English Native Speaker', 'Tham Nien', 'Dia Chi', 'Giao Vien Moi', 'Nhom'])

    # Extract info from excel file
    for i in range(2, df.shape[0]):
        is_new_teacher = isinstance(df.iloc[i, 20], str)
        native = isTeacherNativeNation(df.iloc[i, 2])
        group = rankTeacher(df.iloc[i, 5], native, is_new_teacher)

        giao_vien_chi_tiet.loc[len(giao_vien_chi_tiet.index)] = [
            df.iloc[i, 1], df.iloc[i, 2], native, df.iloc[i, 5], df.iloc[i, 9], is_new_teacher, group]

    # Handling NaN values
    giao_vien_chi_tiet = giao_vien_chi_tiet[giao_vien_chi_tiet['Quoc Tich'].notna(
    )]

    # Retrieving Coordinates
    giao_vien_chi_tiet[['Latitude', 'Longitude']
                       ] = giao_vien_chi_tiet['Dia Chi'].apply(get_coordinates)

    return giao_vien_chi_tiet


def match(school_data, teacher_data) -> bytes:
    df_school = readDataframeFrombase64(school_data['data'])
    df_teacher = readDataframeFrombase64(teacher_data['data'])

    df_school = create_Truong_DataFrame(df_school)
    df_teacher = create_GV_DataFrame(df_teacher)

    print(df_school.head())
    print(df_teacher.head())
    return zipDataFrames([df_school, df_teacher], ["school.xlsx", "teacher.xlsx"])

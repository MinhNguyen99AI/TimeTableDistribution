from common.util import readDataframeFrombase64, zipExporters
from common.constants import *

from resources.services.geocodingService import get_coordinates
import numpy as np
import pandas as pd
import math
from tqdm import tqdm
import os

from resources.services.exporter.schoolDetailExporter import SchoolDetailExporter
from resources.services.exporter.teacherDetailExporter import TeacherDetailExporter
from resources.services.exporter.teacherMasterExporter import TeacherMasterExporter


### API LOCATION ###
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


def preprocess_address(address):
    if isinstance(address, str) == False:
        address = str(address)
    address = address.replace(' HN', 'Hanoi')
    return address


def get_coordinates(address):
    address = preprocess_address(address)
    locator = Nominatim(user_agent="myGeocoder")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    address_piece = address.split(',')
    # print(address_piece)
    for i in range(len(address_piece)):
        # print(address)
        location = geocode(address)
        if location != None:
            return pd.Series([location.latitude, location.longitude])
        else:
            address = address.replace(address_piece[i]+',', '')
    return pd.Series([0, 0])

#### PROCESS TRUONG.xlsx ####


def tu_chon_lich_checker(df):
    if 'Có' in df.iloc[4, 49]:
        return True
    else:
        return False

### RANDOM LICH HOC ###


def check_chuong_trinh(column_number):
    if column_number <= 11:
        return '3 Dai Tra'
    if column_number <= 19:
        return '2 Toan'
    if column_number <= 27:
        return '2 Khoa Hoc'
    if column_number <= 35:
        return '1 Chat Luong Cao'
    else:
        return '2 STEM'


def create_Truong_DataFrame(df):
    thu = [2, 4, 6, 3, 5]
    df['Thu'] = np.tile(thu, len(df)//len(thu) + 1)[:len(df)]
    newdf = df.sort_values(by=['Loai Giao Vien', 'Ten Truong', 'Thu', 'Khoi', 'Lop so'], axis=0, ascending=[True, False, True, True, True], inplace=False,
                           kind='quicksort', na_position='first', ignore_index=True, key=None)
    tietTrongNgay = [1, 2, 3, 4, 5, 6, 7, 8]
    newdf['Tiet_Trong_Ngay'] = 0
    counter = 0
    for i in range(newdf.shape[0]):
        if i > 0:
            if newdf['Thu'][i] != newdf['Thu'][i-1]:
                if counter == 5 and newdf['Ten Truong'][i] == newdf['Ten Truong'][i-1]:
                    newdf.loc[i-1, 'Thu'] = newdf['Thu'][i].copy()
                    newdf.loc[i-1, 'Tiet_Trong_Ngay'] = 1
                    counter = 1
                else:
                    counter = 0
            if newdf['Loai Giao Vien'][i] != newdf['Loai Giao Vien'][i-1]:
                counter = 0
        newdf.loc[i, 'Tiet_Trong_Ngay'] = tietTrongNgay[counter]
        counter += 1
        if counter > 7:
            counter = counter % 8
    finaldf = newdf.sort_values(by=['Loai Giao Vien', 'Ten Truong', 'Thu', 'Khoi', 'Lop so'], axis=0, ascending=[False, False, True, True, True], inplace=False,
                                kind='quicksort', na_position='first', ignore_index=True, key=None)
    return finaldf


def preprocess_Truong_DataFrame(df):
    truong_chi_tiet = pd.DataFrame(columns=['Ten Truong', 'Cap do', 'Khoi', 'Chuong Trinh',
                                   'Lop so', 'Loai Giao Vien', 'Tiet so may trong tuan', 'Extra', 'Document'])
    diachi = pd.DataFrame(
        columns=['Ten Truong', 'Số', 'Phố', 'Phường', 'Quận', 'Thành Phố'])
    current_school = None
    current_priority = None
    khoilist = [4, 12, 20, 28, 36]
    for i in range(0, df.shape[0]):
        for j in range(0, df.shape[1]):
            if j == 3 and isinstance(df.iloc[i, j], str):
                current_school = str(df.iloc[i, j]).strip('\n')
                if isinstance(df.iloc[i, j-1], str) == False and math.isnan(df.iloc[i, j-1]) == False:
                    current_priority = str(int(df.iloc[i, j-1]))
                if isinstance(df.iloc[i, 48], str) == True:
                    diachi.loc[len(diachi.index)] = [current_school, df.iloc[i, 44],
                                                     df.iloc[i, 45], df.iloc[i, 46], df.iloc[i, 47], df.iloc[i, 48]]
            if j in khoilist:
                if isinstance(df.iloc[i, j], str) == False and isinstance(df.iloc[i, j+1], str) == False:
                    if math.isnan(df.iloc[i, j]) == False and math.isnan(df.iloc[i, j+1]) == False:
                        if isinstance(df.iloc[i, j+1], str) == False:
                            for c in range(1, int(df.iloc[i, j+1]) + 1):
                                # GVNN
                                if isinstance(df.iloc[i, j+6], str):
                                    if 'tuần' in df.iloc[i, j+6]:
                                        tiet = int(df.iloc[i, j+6][0])
                                        for t in range(1, tiet+1):
                                            #print(current_school + '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN ' + str(df.iloc[i, j+6]) +'-' + 'GVVN ' + str(df.iloc[i, j+7] ))
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority + '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN tiet so ' + str(t))
                                            truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                                df.iloc[i, j]), check_chuong_trinh(j), c, 'GVNN', t, False, df.iloc[i, j+3]]
                                    if 'tháng' in df.iloc[i, j+6]:
                                        tietthang = int(df.iloc[i, j+6][0])
                                        extra = tietthang % 4
                                        tiettuan = int(tietthang/4)
                                        for t in range(1, tiettuan+1):
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN tiet so ' + str(t))
                                            truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                                df.iloc[i, j]), check_chuong_trinh(j), c, 'GVNN', t, False, df.iloc[i, j+3]]
                                        #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN extra ' + str(extra) +'tiet')
                                        truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                            df.iloc[i, j]), check_chuong_trinh(j), c, 'GVNN', extra, True, df.iloc[i, j+3]]
                                # GVVN
                                if isinstance(df.iloc[i, j+7], str):
                                    if 'tuần' in df.iloc[i, j+7]:
                                        tiet = int(df.iloc[i, j+7][0])
                                        for t in range(1, tiet+1):
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN ' + str(df.iloc[i, j+6]) +'-' + 'GVVN ' + str(df.iloc[i, j+7] ))
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVVN tiet so ' + str(t))
                                            truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                                df.iloc[i, j]), check_chuong_trinh(j), c, 'GVVN', t, False, df.iloc[i, j+3]]
                                    if 'tháng' in df.iloc[i, j+7]:
                                        tietthang = int(df.iloc[i, j+7][0])
                                        extra = tietthang % 4
                                        tiettuan = int(tietthang/4)
                                        for t in range(1, tiettuan+1):
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVVN tiet so ' + str(t))
                                            truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                                df.iloc[i, j]), check_chuong_trinh(j), c, 'GVVN', t, False, df.iloc[i, j+3]]
                                        #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVVN extra ' + str(extra) +'tiet')
                                        truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                            df.iloc[i, j]), check_chuong_trinh(j), c, 'GVVN', extra, True, df.iloc[i, j+3]]
                        else:
                            classes = df.iloc[i, j+1].split(',')
                            for c in classes:
                                # GVNN
                                if isinstance(df.iloc[i, j+6], str):
                                    if 'tuần' in df.iloc[i, j+6]:
                                        tiet = int(df.iloc[i, j+6][0])
                                        for t in range(1, tiet+1):
                                            #print(current_school + '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN ' + str(df.iloc[i, j+6]) +'-' + 'GVVN ' + str(df.iloc[i, j+7] ))
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority + '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN tiet so ' + str(t))
                                            truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                                df.iloc[i, j]), check_chuong_trinh(j), c, 'GVNN', t, False, df.iloc[i, j+3]]
                                    if 'tháng' in df.iloc[i, j+6]:
                                        tietthang = int(df.iloc[i, j+6][0])
                                        extra = tietthang % 4
                                        tiettuan = int(tietthang/4)
                                        for t in range(1, tiettuan+1):
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN tiet so ' + str(t))
                                            truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                                df.iloc[i, j]), check_chuong_trinh(j), c, 'GVNN', t, False, df.iloc[i, j+3]]
                                        #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN extra ' + str(extra) +'tiet')
                                        truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                            df.iloc[i, j]), check_chuong_trinh(j), c, 'GVNN', extra, True, df.iloc[i, j+3]]
                                # GVVN
                                if isinstance(df.iloc[i, j+7], str):
                                    if 'tuần' in df.iloc[i, j+7]:
                                        tiet = int(df.iloc[i, j+7][0])
                                        for t in range(1, tiet+1):
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVNN ' + str(df.iloc[i, j+6]) +'-' + 'GVVN ' + str(df.iloc[i, j+7] ))
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVVN tiet so ' + str(t))
                                            truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                                df.iloc[i, j]), check_chuong_trinh(j), c, 'GVVN', t, False, df.iloc[i, j+3]]
                                    if 'tháng' in df.iloc[i, j+7]:
                                        tietthang = int(df.iloc[i, j+7][0])
                                        extra = tietthang % 4
                                        tiettuan = int(tietthang/4)
                                        for t in range(1, tiettuan+1):
                                            #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVVN tiet so ' + str(t))
                                            truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                                df.iloc[i, j]), check_chuong_trinh(j), c, 'GVVN', t, False, df.iloc[i, j+3]]
                                        #print(current_school + '-'+ 'Cap Do '+ current_priority+ '-'+ 'Khoi '+ str(int(df.iloc[i, j])) + '-' + 'Chuong trinh '+ check_chuong_trinh(j) + '-'+ 'Lop so '+ str(c) + '-'+ 'GVVN extra ' + str(extra) +'tiet')
                                        truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                                            df.iloc[i, j]), check_chuong_trinh(j), c, 'GVVN', extra, True, df.iloc[i, j+3]]
    return create_Truong_DataFrame(truong_chi_tiet), diachi

#### SPECIFY LICH HOC ####


def get_Thu(column):
    if column == 51:
        return 2
    if column == 52:
        return 3
    if column == 53:
        return 4
    if column == 54:
        return 5
    if column == 55:
        return 6


def process_lich(string_lich):
    lich = string_lich.split('-')
    if '' in lich:
        lich.remove('')
    # print(lich)
    khoi = lich[1][0]
    lop_so = lich[1][1:]
    loai_GV = lich[2]
    tai_lieu_index = None
    if lich[0] == 'DT':
        lich[0] = '3 Dai Tra'
        tai_lieu_index = 7
    elif lich[0] == 'TOAN':
        lich[0] = '2 Toan'
        tai_lieu_index = 15
    elif lich[0] == 'KH':
        lich[0] = '2 Khoa Hoc'
        tai_lieu_index = 23
    elif lich[0] == 'CLC':
        lich[0] = '1 Chat Luong Cao'
        tai_lieu_index = 31
    elif lich[0] == 'STEM':
        lich[0] = '2 STEM'
        tai_lieu_index = 39
    chuong_trinh = lich[0]
    return khoi, lop_so, loai_GV, chuong_trinh, tai_lieu_index


def preprocess_Truong_DataFrame_tu_chon_lich(df):
    diachi = pd.DataFrame(
        columns=['Ten Truong', 'Số', 'Phố', 'Phường', 'Quận', 'Thành Phố'])
    truong_chi_tiet = pd.DataFrame(columns=[
                                   'Ten Truong', 'Cap do', 'Khoi', 'Chuong Trinh', 'Lop so', 'Loai Giao Vien', 'Thu', 'Buoi', 'Document'])
    current_school = None
    current_priority = None
    for i in range(0, df.shape[0]):
        if isinstance(df.iloc[i, 3], str):
            current_school = str(df.iloc[i, 3]).strip('\n')
            if isinstance(df.iloc[i, 2], str) == False and math.isnan(df.iloc[i, 2]) == False:
                current_priority = str(int(df.iloc[i, 2]))
            if isinstance(df.iloc[i, 48], str) == True:
                diachi.loc[len(diachi.index)] = [current_school, df.iloc[i, 44],
                                                 df.iloc[i, 45], df.iloc[i, 46], df.iloc[i, 47], df.iloc[i, 48]]
            for j in range(51, 56):
                if isinstance(df.iloc[i, j], str) == True:
                    classes = df.iloc[i, j].replace(' ', '')
                    classes = classes.split(',')
                    for c in range(0, len(classes)):
                        if len(classes[c]) == 0:
                            continue
                        khoi, lop_so, loai_GV, chuong_trinh, tailieu = process_lich(
                            classes[c])
                        truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                            khoi), chuong_trinh, lop_so, loai_GV, get_Thu(j), 0, df.iloc[i + int(khoi) - 1, tailieu]]
                if isinstance(df.iloc[i+1, j], str) == True:
                    classes = df.iloc[i+1, j].replace(' ', '')
                    classes = classes.split(',')
                    for c in range(0, len(classes)):
                        if len(classes[c]) == 0:
                            continue
                        khoi, lop_so, loai_GV, chuong_trinh, tailieu = process_lich(
                            classes[c])
                        truong_chi_tiet.loc[len(truong_chi_tiet.index)] = [current_school, int(current_priority), int(
                            khoi), chuong_trinh, lop_so, loai_GV, get_Thu(j), 1, df.iloc[i + int(khoi) - 1, tailieu]]
    newdf = truong_chi_tiet.sort_values(by=['Loai Giao Vien', 'Ten Truong', 'Thu', 'Buoi', 'Khoi', 'Lop so'], axis=0, ascending=[True, False, True, True, True, True], inplace=False,
                                        kind='quicksort', na_position='first', ignore_index=True, key=None)
    tietTrongNgay = [1, 2, 3, 4]
    newdf['Tiet_Trong_Ngay'] = 0
    counter = 0
    for i in range(newdf.shape[0]):
        if i > 0:
            if newdf['Thu'][i] != newdf['Thu'][i-1]:
                counter = 0
            if newdf['Loai Giao Vien'][i] != newdf['Loai Giao Vien'][i-1]:
                counter = 0
            if newdf['Ten Truong'][i] != newdf['Ten Truong'][i-1]:
                counter = 0
            if newdf['Buoi'][i] != newdf['Buoi'][i-1]:
                counter = 0
        #print(i, newdf.shape[0], counter)
        newdf.loc[i, 'Tiet_Trong_Ngay'] = tietTrongNgay[counter] + \
            newdf['Buoi'][i] * 4
        counter += 1
        if counter > 3:
            counter = counter % 4
    return newdf, diachi


#### PROCESS DIA CHI TRUONG ####
def stringchecker(text):
    while len(text) > 0:
        i = 0
        if text[i] + text[i+1] != ', ':
            return text
        else:
            text = text[2:]


def create_Dia_Chi_Truong_DataFrame(df):
    a = df.fillna('')
    a['DiaChi'] = a['Số'].astype(str) + ', ' + a['Phố'] + ', ' + \
        a['Phường'] + ', ' + a['Quận'] + ', ' + a['Thành Phố']
    a['DiaChi'] = a['DiaChi'].apply(stringchecker)
    a[['Latitude', 'Longitude']] = a['DiaChi'].progress_apply(get_coordinates)
    toa_do_truong = a[['Ten Truong', 'Latitude', 'Longitude']].copy()
    return toa_do_truong

### PROCESS GVVN.xlsx & GVNN.xlsx ###


def create_GV_dataframe(df):
    giao_vien_chi_tiet = df.copy()
    giao_vien_chi_tiet.index = pd.RangeIndex(len(giao_vien_chi_tiet.index))
    giao_vien_chi_tiet.columns = ['Ten GV', 'Dia Chi', 'Nhom']
    giao_vien_chi_tiet.loc[giao_vien_chi_tiet['Nhom'] == 2, 'Nhom'] = 'A'
    giao_vien_chi_tiet.loc[giao_vien_chi_tiet['Nhom'] == 1, 'Nhom'] = 'B'
    giao_vien_chi_tiet.loc[giao_vien_chi_tiet['Nhom'] == 0, 'Nhom'] = 'C'
    giao_vien_chi_tiet.loc[giao_vien_chi_tiet['Nhom'].isnull(), 'Nhom'] = 'C'
    giao_vien_chi_tiet[['Latitude', 'Longitude']
                       ] = giao_vien_chi_tiet['Dia Chi'].progress_apply(get_coordinates)
    return giao_vien_chi_tiet

### MATCHING ###


def same_name_checker(df_GV):
    for i in range(df_GV.shape[0]):
        current_name = df_GV.loc[i, 'Ten GV']
        index = df_GV[df_GV['Ten GV'] == current_name].index
        if len(index) > 1:
            for idx in index:
                df_GV.loc[idx, 'Ten GV'] = df_GV.loc[idx, 'Ten GV'] + str(idx)
    return df_GV


def same_name_checker_truong(df_truong):
    df_truong = df_truong.drop_duplicates(subset=['Ten Truong'])
    return df_truong


def create_matching_GV(df_GV):
    ### Create checker cho tiet va buoi ###
    # GV day 40 tiet 1 tuan
    df_GV['Full'] = 40
    ### Tiet trong tuan danh so tu 1 den 40 ###
    slot = list(range(1, 41))
    df_GV[slot] = False
    ### Buoi trong tuan danh so tu 41 den 50 (tuong ung tu 1 den 10) ###
    slot = list(range(41, 51))
    df_GV[slot] = 'free'
    return df_GV


def cal_distance(cor1, cor2):
    return np.abs(cor1['Latitude'] - cor2['Latitude']) + np.abs(cor1['Longitude'] - cor2['Longitude'])


def construct_distance_matrix(gv, truong_location):
    distance_matrix = pd.DataFrame(
        index=truong_location['Ten Truong'], columns=gv['Ten GV'])
    for i in range(truong_location.shape[0]):
        for j in range(gv.shape[0]):
            distance_matrix.iloc[i, j] = cal_distance(
                gv.iloc[j, :], truong_location.iloc[i, :])
    return distance_matrix


def create_matching_order_truong(df_truong):
    tiet_trong_tuan = df_truong.groupby(['Ten Truong']).size()
    df_truong['Tong so tiet 1 tuan'] = 0
    for i in range(df_truong.shape[0]):
        df_truong.loc[i, 'Tong so tiet 1 tuan'] = tiet_trong_tuan[df_truong.loc[i, 'Ten Truong']]
    matching_order_truong = df_truong[df_truong['Loai Giao Vien'] == 'GVNN']
    matching_order_truong = matching_order_truong.sort_values(by=['Ten Truong', 'Cap do', 'Tong so tiet 1 tuan', 'Thu', 'Tiet_Trong_Ngay'], axis=0, ascending=[True, True, False, True, True], inplace=False,
                                                              kind='quicksort', na_position='first', ignore_index=True, key=None)
    return matching_order_truong


def get_location(data, df_location):
    indexes = (df_location['Ten Truong'] == data)
    return df_location[indexes]['Latitude'].values, df_location[indexes]['Longitude'].values


def make_full_block(teacher_name, ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix):
    #global df_GV
    index = df_GV[df_GV['Ten GV'] == teacher_name].index
    #print('Pass 1.0.1', index)
    drop = False
    for i in range(41, 51):
        if df_GV.loc[index, i].values == ten_truong_da_qua:
            thu = math.ceil((i-40)/2) + 1
            if i % 2 == 0:
                buoi = 1
            else:
                buoi = 0
            for j in range(1, 5):
                if df_GV.loc[index, 8*(thu-2) + j + 4*buoi].values == False:
                    df_GV.loc[index, 8*(thu-2) + j + 4*buoi] = True
                    drop, df_GV, distance_matrix = check_teacher_full(
                        teacher_name, df_GV, distance_matrix)
                    #print('Pass 1.0.2')
                    if drop:
                        break
            if drop:
                break
    return df_GV, distance_matrix, drop


def check_teacher_slot(teacher_name, thu, tiet_trong_ngay, school_name, df_GV):
    #global df_GV
    if tiet_trong_ngay > 4:
        buoi = 0
    else:
        buoi = 1
    slot_buoi = (thu-1)*2 - buoi
    index = df_GV[df_GV['Ten GV'] == teacher_name].index
    if df_GV.loc[index, 8*(thu-2) + tiet_trong_ngay].values == True:
        return False, df_GV
    elif df_GV.loc[index, 40 + slot_buoi].values != school_name and df_GV.loc[index,    40 + slot_buoi].values != 'free':
        return False, df_GV
    else:
        df_GV.loc[index, 8*(thu-2) + tiet_trong_ngay] = True
        df_GV.loc[index, 40 + slot_buoi] = school_name
        return True, df_GV


def check_teacher_full(teacher_name, df_GV, distance_matrix):
    #global df_GV, distance_matrix
    index = df_GV[df_GV['Ten GV'] == teacher_name].index
    df_GV.loc[index, 'Full'] = df_GV.loc[index, 'Full'].copy() - 1
    if df_GV.loc[index, 'Full'].values == 0:
        df_GV = df_GV.drop(index)
        distance_matrix = distance_matrix.drop(columns=teacher_name)
        return True, df_GV, distance_matrix
    return False, df_GV, distance_matrix


def match_teacher(index, ten_truong_hien_tai, ten_truong_da_qua, distance_matrix, df_GV, matching_order_truong):
    #global ten_truong_hien_tai, ten_truong_da_qua

    ten_truong = matching_order_truong.loc[index, 'Ten Truong']
    ten_truong_hien_tai = ten_truong
    if ten_truong_da_qua != None:
        if ten_truong_da_qua != ten_truong_hien_tai:
            #print('Pass 1')
            # for a in range(0, df_GV.shape[0]):
            #     if a >= df_GV.shape[0]:
            #         break
            #     df_GV.index = pd.RangeIndex(len(df_GV.index))
            #     df_GV, distance_matrix, drop = make_full_block(df_GV.loc[a, 'Ten GV'], ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix)
            a = 0
            while a < df_GV.shape[0]:
                df_GV.index = pd.RangeIndex(len(df_GV.index))
                df_GV, distance_matrix, drop = make_full_block(
                    df_GV.loc[a, 'Ten GV'], ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix)
                if drop:
                    continue
                else:
                    a += 1
    #print('Pass 1.1')
    ten_truong_da_qua = ten_truong_hien_tai
    thu = matching_order_truong.loc[index, 'Thu']
    tiet_trong_ngay = matching_order_truong.loc[index, 'Tiet_Trong_Ngay']
    #print('Pass 1.2')
    index_A = (df_GV[df_GV['Nhom'] == 'A'])
    index_B = (df_GV[df_GV['Nhom'] == 'B'])
    index_C = (df_GV[df_GV['Nhom'] == 'C'])
    a = 0
    a_flag = False
    b = 0
    b_flag = False
    c = 0
    c_flag = False
    while len(index_A) > 0:
        ten_GV_A = distance_matrix.loc[ten_truong,
                                       index_A['Ten GV']].sort_values()
        #print('Pass 2')
        con_slot, df_GV = check_teacher_slot(
            ten_GV_A.index[a], thu, tiet_trong_ngay, ten_truong, df_GV)
        while con_slot == False:
            a += 1
            if a >= len(index_A):
                a_flag = True
                break
            con_slot, df_GV = check_teacher_slot(
                ten_GV_A.index[a], thu, tiet_trong_ngay, ten_truong, df_GV)
        if a_flag:
            break
        else:
            full_slot, df_GV, distance_matrix = check_teacher_full(
                ten_GV_A.index[a], df_GV, distance_matrix)
            return ten_GV_A.index[a], ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix
    while len(index_B) > 0:
        ten_GV_B = distance_matrix.loc[ten_truong,
                                       index_B['Ten GV']].sort_values()
        #print('Pass 2')
        con_slot, df_GV = check_teacher_slot(
            ten_GV_B.index[b], thu, tiet_trong_ngay, ten_truong, df_GV)
        while con_slot == False:
            b += 1
            if b >= len(index_B):
                b_flag = True
                break
            con_slot, df_GV = check_teacher_slot(
                ten_GV_B.index[b], thu, tiet_trong_ngay, ten_truong, df_GV)
        if b_flag:
            break
        else:
            full_slot, df_GV, distance_matrix = check_teacher_full(
                ten_GV_B.index[b], df_GV, distance_matrix)
            return ten_GV_B.index[b], ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix
    while len(index_C) > 0:
        ten_GV_C = distance_matrix.loc[ten_truong,
                                       index_C['Ten GV']].sort_values()
        #print('Pass 2')
        con_slot, df_GV = check_teacher_slot(
            ten_GV_C.index[c], thu, tiet_trong_ngay, ten_truong, df_GV)
        while con_slot == False:
            c += 1
            if c >= len(index_C):
                c_flag = True
                break
            con_slot, df_GV = check_teacher_slot(
                ten_GV_C.index[c], thu, tiet_trong_ngay, ten_truong, df_GV)
        if c_flag:
            break
        else:
            full_slot, df_GV, distance_matrix = check_teacher_full(
                ten_GV_C.index[c], df_GV, distance_matrix)
            return ten_GV_C.index[c], ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix
    return 'THIEU GIAO VIEN', ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix

#### GVVN ####


def create_matching_order_truong_VIETNAM(df_truong):
    tiet_trong_tuan = df_truong.groupby(['Ten Truong']).size()
    df_truong['Tong so tiet 1 tuan'] = 0
    for i in range(df_truong.shape[0]):
        df_truong.loc[i, 'Tong so tiet 1 tuan'] = tiet_trong_tuan[df_truong.loc[i, 'Ten Truong']]
    matching_order_truong = df_truong[df_truong['Loai Giao Vien'] == 'GVVN']
    matching_order_truong = matching_order_truong.sort_values(by=['Ten Truong', 'Cap do', 'Tong so tiet 1 tuan', 'Thu', 'Tiet_Trong_Ngay'], axis=0, ascending=[True, True, False, True, True], inplace=False,
                                                              kind='quicksort', na_position='first', ignore_index=True, key=None)
    return matching_order_truong


def run(df_truong, df_GVNN, df_GVVN):
    ##### MATCHING GVNN #####
    #### check if tu chon lich ####
    if tu_chon_lich_checker(df_truong) == True:
        df_truong_processed, df_diachitruong = preprocess_Truong_DataFrame_tu_chon_lich(
            df_truong)
    else:
        df_truong_processed, df_diachitruong = preprocess_Truong_DataFrame(
            df_truong)

    # Retrieve toa do #
    print("Start coordinate school")
    df_location = create_Dia_Chi_Truong_DataFrame(df_diachitruong)
    df_location = same_name_checker_truong(df_location)
    print("Finished coordinate school")
    ### GVNN ###

    # Retrieve distance matrix cho GVNN
    print("Start coordinate foreign teacher")
    df_GV = create_matching_GV(create_GV_dataframe(df_GVNN))
    df_GV = same_name_checker(df_GV)
    distance_matrix = construct_distance_matrix(df_GV, df_location)
    print("Finished coordinate foreign teacher")

    matching_order_truong = create_matching_order_truong(df_truong_processed)

    ten_truong_hien_tai = None
    ten_truong_da_qua = None
    matching_order_truong['Ten Giao Vien Duoc Xep'] = 'CHUA DUOC XEP'
    matching_order_truong['index'] = matching_order_truong.index
    for i in tqdm(range(0, matching_order_truong.shape[0])):
        matching_order_truong.loc[i, 'Ten Giao Vien Duoc Xep'], ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix = match_teacher(
            matching_order_truong.loc[i, 'index'], ten_truong_hien_tai, ten_truong_da_qua, distance_matrix, df_GV, matching_order_truong)
        # print(df_GV.shape)
    matching_order_truong = matching_order_truong.sort_values(by=['Cap do', 'Tong so tiet 1 tuan', 'Thu', 'Tiet_Trong_Ngay', 'Lop so'], axis=0, ascending=[True, False, True, True, True], inplace=False,
                                                              kind='quicksort', na_position='first', ignore_index=True, key=None)

    gvnn_result = matching_order_truong.copy()

    #### MATCHING GVVN ####

    # Retrieve distance matrix cho GVVN
    print("Start coordinate domestic teacher")
    df_GV = create_matching_GV(create_GV_dataframe(df_GVVN))
    df_GV = same_name_checker(df_GV)
    distance_matrix = construct_distance_matrix(df_GV, df_location)
    print("Finished coordinate domestic teacher")

    matching_order_truong = create_matching_order_truong_VIETNAM(
        df_truong_processed)

    ten_truong_hien_tai = None
    ten_truong_da_qua = None

    matching_order_truong['Ten Giao Vien Duoc Xep'] = 'CHUA DUOC XEP'
    matching_order_truong['index'] = matching_order_truong.index
    for i in tqdm(range(0, matching_order_truong.shape[0])):
        matching_order_truong.loc[i, 'Ten Giao Vien Duoc Xep'], ten_truong_hien_tai, ten_truong_da_qua, df_GV, distance_matrix = match_teacher(
            matching_order_truong.loc[i, 'index'], ten_truong_hien_tai, ten_truong_da_qua, distance_matrix, df_GV, matching_order_truong)
    matching_order_truong = matching_order_truong.sort_values(by=['Cap do', 'Tong so tiet 1 tuan', 'Thu', 'Tiet_Trong_Ngay', 'Lop so'], axis=0, ascending=[True, False, True, True, True], inplace=False,
                                                              kind='quicksort', na_position='first', ignore_index=True, key=None)

    gvvn_result = matching_order_truong.copy()
    return gvnn_result, gvvn_result


def match(school_data, teacher_domestic_data, teacher_foreign_data) -> bytes:
    tqdm.pandas()
    df_truong = readDataframeFrombase64(school_data['data'])
    df_GVVN = readDataframeFrombase64(
        teacher_domestic_data['data'])
    df_GVNN = readDataframeFrombase64(teacher_foreign_data['data'])
    print("Done read input")

    gvnn_result, gvvn_result = run(df_truong, df_GVNN, df_GVVN)
    print("Finished main process, writing to files...")
    # gvnn_result = pd.read_excel("D:/Projects/[RESULTS] GVNN.xlsx")
    # gvvn_result = pd.read_excel("D:/Projects/[RESULTS] GVVN.xlsx")

    df_all_result = pd.concat([gvnn_result, gvvn_result]).reset_index()

    school_detail = SchoolDetailExporter(
        df_all_result, "TKB chi tiết trường.xlsx")

    gvnn_detail = TeacherDetailExporter(
        gvnn_result, "TKB GVNN - chi tiết.xlsx")
    gvnn_master = TeacherMasterExporter(
        gvnn_result, "TKB GVNN - tổng.xlsx")

    gvvn_detail = TeacherDetailExporter(
        gvvn_result, "TKB GVVN - chi tiết.xlsx")
    gvvn_master = TeacherMasterExporter(
        gvvn_result, "TKB GVVN - tổng.xlsx")

    return zipExporters([school_detail, gvnn_detail, gvnn_master, gvvn_detail, gvvn_master])

from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
import pandas as pd
import math


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
        a['Phường (Nếu có)'] + ', ' + a['Quận'] + ', ' + a['Thành Phố']
    a['DiaChi'] = a['DiaChi'].apply(stringchecker)
    a[['Latitude', 'Longitude']] = a['DiaChi'].apply(get_coordinates)
    toa_do_truong = a[['Ten Truong', 'Latitude', 'Longitude']].copy()
    return toa_do_truong


# Process input file danh sach GV
def create_GV_DataFrame(df):
    # create dataframe
    giao_vien_chi_tiet = pd.DataFrame(columns=[
                                      'Ten GV', 'Quoc Tich', 'English Native Speaker', 'Tham Nien', 'Dia Chi', 'Giao Vien Moi', 'Nhom'])

    # Extract info from excel file
    for i in range(2, df.shape[0]):
        group = None
        native = None
        newTeacher = isinstance(df.iloc[i, 20], str)
        if df.iloc[i, 2] in ['Anh', 'Ai-len', 'Mỹ', 'Ai-Len', 'Nam Phi', 'Úc', 'Đan Mạch', 'Ailen', 'Ấn Độ', 'Hungari', 'Canada', 'Italy', 'Thuỵ Điển', 'Ý']:
            native = True
        elif df.iloc[i, 2] in ['Ai Cập', 'Thổ Nhĩ Kỳ', 'Pháp', 'Ukraine', 'Hy Lạp', 'Brasil', 'Morocco', 'Croatia', 'Russia', 'Ba Lan', 'Nga', 'Zimbabwean',  'Colombia']:
            native = False
        else:
            native = None
        if isinstance(df.iloc[i, 5], str) == False:
            if math.isnan(df.iloc[i, 5], ) == False:
                if int(df.iloc[i, 5]) >= 2 and native == True and newTeacher == False:
                    group = 'A'
                elif int(df.iloc[i, 5]) >= 1 and newTeacher == False:
                    group = 'B'
                else:
                    group = 'C'
        if group == None:
            group = 'C'
        giao_vien_chi_tiet.loc[len(giao_vien_chi_tiet.index)] = [
            df.iloc[i, 1], df.iloc[i, 2], native, df.iloc[i, 5], df.iloc[i, 9], newTeacher, group]

    # Handling NaN values
    giao_vien_chi_tiet = giao_vien_chi_tiet[giao_vien_chi_tiet['Quoc Tich'].notna(
    )]

    # Retrieving Coordinates
    giao_vien_chi_tiet[['Latitude', 'Longitude']
                       ] = giao_vien_chi_tiet['Dia Chi'].apply(get_coordinates)

    # Return dataframe
    return giao_vien_chi_tiet

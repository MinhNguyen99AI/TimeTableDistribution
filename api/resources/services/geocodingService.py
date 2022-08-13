from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
import pandas as pd


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

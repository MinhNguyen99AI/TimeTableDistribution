from io import BytesIO
from wsgiref import headers
import pandas as pd
import base64


def readDataframeFrombase64(data: str, sheetName: str = None):
    bytes_data = base64.b64decode(data)

    df = pd.read_excel(BytesIO(bytes_data))
    return df

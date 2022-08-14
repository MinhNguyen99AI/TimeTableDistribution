from io import BytesIO
from typing import List
import pandas as pd
import base64
from zipfile import ZipFile
import io


def readDataframeFrombase64(data: str, sheetName: str = None) -> pd.DataFrame:
    bytes_data = base64.b64decode(data)

    df = pd.read_excel(BytesIO(bytes_data))
    return df


def zipExporters(exporters) -> bytes:
    memfile = io.BytesIO()
    with ZipFile(memfile, mode='w') as zf:
        for exporter in exporters:
            with zf.open(exporter.getName(), "w") as buffer:
                exporter.process(buffer)
    return memfile.getvalue()


def isOneVal(s: pd.DataFrame):
    a = s.to_numpy()
    return (a[0] == a).all()


def copyFormat(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    return book.add_format({k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})


def getDayFromNum(dayNum):
    if dayNum == 2:
        return "Monday"

    if dayNum == 3:
        return "Tuesday"

    if dayNum == 4:
        return "Wednesday"

    if dayNum == 5:
        return "Thursday"

    if dayNum == 6:
        return "Friday"

    if dayNum == 7:
        return "Saturday"
    return "Sunday"

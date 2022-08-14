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

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


def zipDataFrames(dfs: List[pd.DataFrame], names: List[str]) -> bytes:
    if len(dfs) != len(names):
        raise ValueError("Df and names length do not match")

    memfile = io.BytesIO()
    with ZipFile(memfile, mode='w') as zf:
        for df, name in zip(dfs, names):
            with zf.open(name, "w") as buffer:
                df.to_excel(buffer, index=False)
    return memfile.getvalue()

import json

import numpy as np
import pandas as pd


def prepare_dict(d: dict) -> dict:
    result = {}
    for k, v in d.items():
        if isinstance(v, (float, np.floating)):
            v = float(v)
        elif isinstance(v, dict):
            v = prepare_dict(v)
        result[k] = v
    return result


def normalize_col(source: pd.DataFrame, name: str) -> pd.DataFrame:
    s = source[name].map(json.loads)
    df = pd.json_normalize(s)
    df.columns = name + '_' + df.columns
    return df


def postprocess_df(df: pd.DataFrame, normalize: bool) -> pd.DataFrame:
    if normalize:
        df = pd.concat([
            df,
            normalize_col(df, 'params'),
            normalize_col(df, 'metrics'),
        ], axis=1)
        df.drop(columns=['params', 'metrics'], inplace=True)
    return df

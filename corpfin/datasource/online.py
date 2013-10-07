import pandas as pd
from pandas.io.data import DataReader, get_components_yahoo

def _ohlc(code, source='yahoo', start=None, end=None):
    df = DataReader(code, source, start=start, end=end)
    df.columns = [c.replace(' ', '_').lower() for c in df.columns]
    return df

def ohlc(codes, source='yahoo', start=None, end=None):
    if isinstance(codes, str):
        return _ohlc(codes, source, start, end)
    elif len(codes) == 1:
        return _ohlc(codes[0], source, start, end)
    else:
        ohlcs = {code: _ohlc(code, source, start, end) for code in codes}
        return pd.Panel(ohlcs)

def idx_components(idx):
    return get_components_yahoo(idx)




if __name__ == '__main__':
    print(ohlc('AAPL'))
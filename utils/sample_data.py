import pandas as pd

def get_traverse_sample():
    data = {'code': ['A', 'B', 'C', 'D'], 'bearing': [90, 180, 270, 0], 'distance': [100, 100, 100, 100]}
    return pd.DataFrame(data).to_csv(index=False).encode('utf-8')

def get_leveling_sample():
    data = {
        'Station': ['BM1', 'P1', 'P2', 'TBM'],
        'BS': [1.500, None, None, None],
        'IS': [None, 1.200, 1.800, None],
        'FS': [None, None, None, 1.400]
    }
    return pd.DataFrame(data).to_csv(index=False).encode('utf-8')

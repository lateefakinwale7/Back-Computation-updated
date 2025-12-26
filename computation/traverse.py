import pandas as pd
import numpy as np

def compute_lat_depart(df):
    df = df.copy()
    # Remove existing calc columns to prevent "InvalidIndexError"
    cols_to_clean = ['Math_Lat', 'Math_Dep', 'Lat (ΔN)', 'Dep (ΔE)', 'Final_N', 'Final_E']
    df = df.drop(columns=[c for c in cols_to_clean if c in df.columns], errors='ignore')
    
    df['Lat (ΔN)'] = df['distance'] * np.cos(np.radians(df['bearing']))
    df['Dep (ΔE)'] = df['distance'] * np.sin(np.radians(df['bearing']))
    return df

def bowditch_adjustment_with_steps(df, start_x, start_y, close_loop):
    df = df.copy()
    total_dist = df['distance'].sum()
    mis_n = df['Lat (ΔN)'].sum()
    mis_e = df['Dep (ΔE)'].sum()
    
    # Linear Misclosure & Precision
    lin_mis = np.sqrt(mis_n**2 + mis_e**2)
    prec = total_dist / lin_mis if lin_mis != 0 else 0
    
    df['Corr_Lat'] = -(mis_n / total_dist) * df['distance']
    df['Corr_Dep'] = -(mis_e / total_dist) * df['distance']
    
    df['Final_N'] = start_y + (df['Lat (ΔN)'] + df['Corr_Lat']).cumsum()
    df['Final_E'] = start_x + (df['Dep (ΔE)'] + df['Corr_Dep']).cumsum()
    
    if close_loop:
        close_row = df.iloc[[0]].copy()
        close_row['code'] = "CLOSE"
        close_row['Final_E'], close_row['Final_N'] = start_x, start_y
        df = pd.concat([df, close_row], ignore_index=True)
        
    return df, mis_n, mis_e, total_dist, prec

def calculate_area(df):
    x, y = df['Final_E'].values, df['Final_N'].values
    area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    return area, area/10000, area/4046.86

def compute_leveling(df, start_rl):
    df = df.copy()
    results = []
    current_rl = start_rl
    for i in range(len(df)):
        row = df.iloc[i].to_dict()
        if i == 0:
            row.update({'Rise': 0, 'Fall': 0, 'RL': current_rl})
        else:
            prev = df.iloc[i-1]
            prev_val = prev['BS'] if pd.notnull(prev['BS']) else prev['IS']
            curr_val = row['IS'] if pd.notnull(row['IS']) else row['FS']
            diff = prev_val - curr_val
            row['Rise'] = diff if diff > 0 else 0
            row['Fall'] = abs(diff) if diff < 0 else 0
            current_rl += (row['Rise'] - row['Fall'])
            row['RL'] = current_rl
        results.append(row)
    return pd.DataFrame(results)

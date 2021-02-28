"""Preprocess replay data to filter out columns unrelated to the bloodsky berserker analysis"""

import argparse
import pandas as pd

import dtypes

parser = argparse.ArgumentParser()
parser.add_argument('--in', dest='input')
parser.add_argument('--out')
args = parser.parse_args()

df = pd.read_csv(args.input, dtype=dtypes.get_dtypes())

# Extract cast/grown columns
cast_cols = []
grown_cols = []
total_cols = []
for player in ['user', 'oppo']:
  for turn in range(1, 31):
    cast_col = f'{player}_turn_{turn}_berserkers_cast'
    df[cast_col] = df[f'{player}_turn_{turn}_creatures_cast'].str.count('75119').fillna(value=0)
    cast_cols.append(cast_col)

    grown_col = f'{player}_turn_{turn}_berserkers_grown'
    df[grown_col] = df[f'{player}_turn_{turn}_abilities'].str.count('139923').fillna(value=0)
    grown_cols.append(grown_col)

  df[f'{player}_total_berserkers_cast'] = df.filter(regex=f'{player}_.*_berserkers_cast', axis=1).sum(axis=1)
  df[f'{player}_total_berserkers_grown'] = df.filter(regex=f'{player}_.*_berserkers_grown', axis=1).sum(axis=1)
  total_cols.extend([f'{player}_total_berserkers_cast', f'{player}_total_berserkers_grown'])

df2 = df[list(dtypes.BASE_COLS.keys()) + cast_cols + grown_cols + total_cols]
df2.to_csv(args.out, index=False)

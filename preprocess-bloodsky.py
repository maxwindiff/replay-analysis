"""Preprocess replay data to filter out columns unrelated to the bloodsky berserker analysis"""

import argparse
import pandas as pd

import dtypes

parser = argparse.ArgumentParser()
parser.add_argument('--in', dest='input')
parser.add_argument('--out')
args = parser.parse_args()

df = pd.read_csv(args.input, dtype=dtypes.get_dtypes())

# Extract cast/growth columns
per_turn_cols = []
total_cols = []
for player in ['user', 'oppo']:
  for turn in range(1, 31):
    berserker_cast_col = f'{player}_turn_{turn}_berserkers_cast'
    df[berserker_cast_col] = df[f'{player}_turn_{turn}_creatures_cast'].str.count('75119').fillna(value=0)

    berserker_growth_col = f'{player}_turn_{turn}_berserkers_growth'
    df[berserker_growth_col] = df[f'{player}_turn_{turn}_abilities'].str.count('139923').fillna(value=0)

    per_turn_cols.extend([
      berserker_cast_col,
      berserker_growth_col,
      f'{player}_turn_{turn}_creatures_cast',
      f'{player}_turn_{turn}_non_creatures_cast',
      f'{player}_turn_{turn}_instants_sorceries_cast',
    ])

  df[f'{player}_total_berserkers_cast'] = df.filter(regex=f'{player}_.*_berserkers_cast', axis=1).sum(axis=1)
  df[f'{player}_total_berserkers_growth'] = df.filter(regex=f'{player}_.*_berserkers_growth', axis=1).sum(axis=1)
  total_cols.extend([f'{player}_total_berserkers_cast', f'{player}_total_berserkers_growth'])

df2 = df[list(dtypes.BASE_COLS.keys()) + per_turn_cols + total_cols]
df2.to_csv(args.out, index=False)

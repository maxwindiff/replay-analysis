import argparse
import string

import numpy as np
import pandas as pd

import dtypes

pd.set_option('display.max_rows', 50)

parser = argparse.ArgumentParser()
parser.add_argument('--cards')
parser.add_argument('--replay')
args = parser.parse_args()

card_data = pd.read_csv(args.cards, header=0, index_col=0, names=[
  'arena_id', 'multiverse_id', 'name', 'cmc', 'color', 'cost', 'produces', 'types', 'rarity', 'unknwon', 'image'
])

dtypes = dtypes.get_dtypes()
for player in ['user', 'oppo']:
  for turn in range(1, 31):
    dtypes.update({
    f'{player}_turn_{turn}_berserkers_cast': int,
    f'{player}_turn_{turn}_berserkers_growth': int,
  })
  dtypes.update({
    f'{player}_total_berserkers_cast': int,
    f'{player}_total_berserkers_growth': int,
  })
df = pd.read_csv(args.replay, dtype=dtypes)

for player in ['user']:
  for turn in range(1, 31):
    df[f'{player}_turn_{turn}_creatures_cast'].fillna(value='', inplace=True)
    df[f'{player}_turn_{turn}_non_creatures_cast'].fillna(value='', inplace=True)
    df[f'{player}_turn_{turn}_instants_sorceries_cast'].fillna(value='', inplace=True)

  grouped = df.groupby(f'{player}_deck_colors')

  summary = pd.concat([
    grouped.size().rename('count'),
    grouped[[f'{player}_total_berserkers_cast', f'{player}_total_berserkers_growth']].sum(),
  ], axis=1)
  print(summary.sort_values(f'{player}_total_berserkers_cast', ascending=False).head(10))

  sums = summary.sum()
  print(f'Overall {player}_total_berserkers_cast = {sums[f"{player}_total_berserkers_cast"]}')
  print(f'Overall {player}_total_berserkers_growth = {sums[f"{player}_total_berserkers_growth"]}')

  played = df[df[f'{player}_total_berserkers_cast'] > 0]
  print(f'Number of games where berserkers were cast = {len(played.index)}')

  growth_groups = played.groupby(f'{player}_total_berserkers_growth')
  growth_stats = pd.concat([
    growth_groups.size().rename('count'),
    growth_groups[f'{player}_total_berserkers_cast'].mean(),
    growth_groups['won'].mean(),
  ], axis=1)
  print(growth_stats)

  growth_spells = {}
  for i, game in played.iterrows():
    for turn in range(1, 31):
      num_cast = game[f'{player}_turn_{turn}_berserkers_cast']
      num_growth = game[f'{player}_turn_{turn}_berserkers_growth']
      if num_growth > 0:
        for spell in game[f'{player}_turn_{turn}_creatures_cast'].split('|') + \
          game[f'{player}_turn_{turn}_non_creatures_cast'].split('|') + \
          game[f'{player}_turn_{turn}_instants_sorceries_cast'].split('|'):
          if spell:
            growth_spells[int(spell)] = growth_spells.get(int(spell), 0) + 1
  growth_spells.pop(75119, None)

  growth = pd.DataFrame(growth_spells, index=['count']).transpose().join(card_data[['name', 'cmc']])
  growth = growth.sort_values('count', ascending=False)
  print(growth.head(20))

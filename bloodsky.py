import argparse
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dtypes

def to_turn_number(col):
  return int(re.findall(r'\d+', col)[0])

pd.set_option('display.max_rows', 50)

parser = argparse.ArgumentParser()
parser.add_argument('--cards')
parser.add_argument('--replay')
args = parser.parse_args()

card_data = pd.read_csv(args.cards, header=0, index_col=0, names=[
  'arena_id', 'multiverse_id', 'name', 'cmc', 'color', 'cost', 'produces', 'types', 'rarity', 'is_booster', 'image'
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
  # Berserkers cast/grown by deck colors
  by_deck_colors = df.groupby(f'{player}_deck_colors')
  summary = pd.concat([
    by_deck_colors.size().rename('count'),
    by_deck_colors[f'{player}_total_berserkers_cast'].sum(),
    by_deck_colors[f'{player}_total_berserkers_growth'].sum(),
  ], axis=1)
  summary.columns = ['count', 'berserkers_cast', 'num_growth_events']
  summary = summary.sort_values('berserkers_cast', ascending=False)

  summary_trimmed = summary.head(10).copy()
  summary_trimmed.loc['Total'] = summary.sum()
  summary_trimmed['ratio'] = summary_trimmed['num_growth_events'] / summary_trimmed['berserkers_cast']
  print(summary_trimmed)

  # Total berserkers cast/grown
  num_games = (df[f"{player}_total_berserkers_cast"] > 0).astype(int).sum()
  print(f'Number of games berserkers were cast = {num_games} ({100 * num_games / len(df.index)}%)')

  # Berserkers cast/grown turns
  cumulative_cast_grown = pd.concat([
    df.filter(regex='user_turn_.*_berserkers_cast').sum().cumsum().rename(index=to_turn_number),
    df.filter(regex='user_turn_.*_berserkers_growth').sum().cumsum().rename(index=to_turn_number),
  ], axis=1)[0:20]
  cumulative_cast_grown.columns = ['cast', 'growth']
  print(cumulative_cast_grown)
  cumulative_cast_grown.plot(kind='bar')

  # Baseline double spell vs win rate
  for turn in range(1, 31):
    df[f'{player}_turn_{turn}_spells_count'] = \
      df[f'{player}_turn_{turn}_creatures_cast'].str.split('|').map(lambda x: len(x) if isinstance(x, list) else 0) + \
      df[f'{player}_turn_{turn}_non_creatures_cast'].str.split('|').map(lambda x: len(x) if isinstance(x, list) else 0) + \
      df[f'{player}_turn_{turn}_instants_sorceries_cast'].str.split('|').map(lambda x: len(x) if isinstance(x, list) else 0)
    df[f'{player}_turn_{turn}_double_spell'] = (df[f'{player}_turn_{turn}_spells_count'] > 1).astype(int)
  df[f'{player}_total_double_spell_turns'] = df.filter(regex=f'{player}_turn_.*_double_spell').sum(axis=1)

  by_double_spell = df.groupby(f'{player}_total_double_spell_turns')
  double_spell_plot = pd.concat([
    by_double_spell.size().rename('count'),
    by_double_spell['won'].mean()],
  axis=1)
  double_spell_plot = double_spell_plot[double_spell_plot['count'] >= 500]
  print(double_spell_plot)
  #p = double_spell_plot.reset_index().plot.scatter(x=f'{player}_total_double_spell_turns', y='won')
  #p.set_ylim(0.25, 0.75)

  # Stats related to games when the berserker is played or grown
  played = df[df[f'{player}_total_berserkers_cast'] > 0].fillna(value='')
  grown = df[df[f'{player}_total_berserkers_growth'] > 0].fillna(value='')

  # Berserker growth vs win rate
  growth_groups = played.groupby(f'{player}_total_berserkers_growth')
  growth_stats = pd.concat([
    growth_groups.size().rename('count'),
    growth_groups['won'].mean(),
  ], axis=1)
  print(growth_stats)

  # Spells triggering berserker growth
  for color in ('WB', 'BR', 'BG'):
    growth_spells = {}
    for i, game in played[played[f'{player}_deck_colors'] == color].iterrows():
      for turn in range(1, 31):
        num_cast = game[f'{player}_turn_{turn}_berserkers_cast']
        num_growth = game[f'{player}_turn_{turn}_berserkers_growth']
        if num_growth > 0:
          for spell in game[f'{player}_turn_{turn}_creatures_cast'].split('|') + \
            game[f'{player}_turn_{turn}_non_creatures_cast'].split('|') + \
            game[f'{player}_turn_{turn}_instants_sorceries_cast'].split('|'):
            if spell:
              growth_spells[int(spell)] = growth_spells.get(int(spell), 0) + 1
    growth_spells.pop(75119, None) # exclude the berserker itself

    growth = pd.DataFrame(growth_spells, index=['count']).transpose().join(card_data[['name', 'cmc']])
    growth = growth.sort_values('count', ascending=False)
    print(f'Spells triggering berserker grown in {color} ({summary.loc[color]["num_growth_events"]} growth events):')
    print(growth.head(10))

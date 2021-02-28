"""Replay data dtypes for pandas"""

BASE_COLS = {
  'history_id': int,
  'time': str,
  'expansion': str,
  'format': str,
  'user_rank': str,
  'oppo_rank': str,
  'game_index': int,
  'user_deck_colors': str,
  'oppo_deck_colors': str,
  'user_mulligans': int,
  'oppo_mulligans': int,
  'on_play': bool,
  'turns': int,
  'won': bool,
  'missing_diffs': int,
}

PER_TURN_COLS = {
  'cards_drawn': str,
  'cards_discarded': str,
  'lands_played': str,
  'creatures_cast': str,
  'non_creatures_cast': str,
  'instants_sorceries_cast': str,
  'abilities': str,
  'cards_foretold': str,
  'creatures_attacked': str,
  'creatures_blocked': str,
  'creatures_unblocked': str,
  'creatures_blocking': str,
  'player_combat_damage_dealt': int,
  'user_creatures_killed_combat': str,
  'oppo_creatures_killed_combat': str,
  'user_creatures_killed_non_combat': str,
  'oppo_creatures_killed_non_combat': str,
  'user_mana_spent': int,
  'oppo_mana_spent': int,
  'eot_user_cards_in_hand': str,
  'eot_oppo_cards_in_hand': str,
  'eot_user_lands_in_play': str,
  'eot_oppo_lands_in_play': str,
  'eot_user_creatures_in_play': str,
  'eot_oppo_creatures_in_play': str,
  'eot_user_non_creatures_in_play': str,
  'eot_oppo_non_creatures_in_play': str,
  'eot_user_life': int,
  'eot_oppo_life': int,
}

SUMMARY_COLS = {
  'cards_drawn': int,
  'cards_discarded': int,
  'lands_played': int,
  'creatures_cast': int,
  'non_creatures_cast': int,
  'instants_sorceries_cast': int,
  'cards_foretold': int,
  'mana_spent': int,
}

def get_dtypes():
  dtypes = BASE_COLS.copy()

  for turn in range(1, 31):
    for player in ['user', 'oppo']:
      for k, v in PER_TURN_COLS.items():
        dtypes[f'{player}_turn_{turn}_{k}'] = v
      dtypes[f'{player}_turn_{turn}_eot_oppo_cards_in_hand'] = int
    dtypes[f'oppo_turn_{turn}_cards_drawn'] = int

  for player in ['user', 'oppo']:
    for col in SUMMARY_COLS:
      dtypes[f'{player}_total_{col}'] = int

  return dtypes

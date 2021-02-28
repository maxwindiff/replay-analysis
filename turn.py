"""Compares turn count recorded from game end result vs turn count inferred from replay history"""

import csv
import fileinput

reader = csv.reader(fileinput.input())

c = {}
header = next(reader)
for i, col in enumerate(header):
  c[col] = i

for row in reader:
  max_turns = 0

  for turn in range(30, 0, -1):
    if row[c[f'user_turn_{turn}_cards_drawn']] != '' or row[c[f'oppo_turn_{turn}_cards_drawn']] != '0':
      max_turns = 2 * turn
      break

  recorded_turns = int(row[c['turns']])
  if abs(max_turns - recorded_turns) > 1:
    print(row[c['history_id']], recorded_turns, max_turns)

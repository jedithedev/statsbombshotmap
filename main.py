from statsbombpy import sb
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import json

match_id = 3890561
team = 'Schalke 04'
lineups = sb.lineups(match_id=match_id)
teamlineup = lineups[team]

shots = sb.events(match_id=match_id, split='true')['shots']
shotsjson = shots.to_json('shots.json', indent=4)

shotsdict = json.loads(open('shots.json', 'r').read())
formattedshotsdict = {}

for key in shotsdict:
    for i in shotsdict[key]:
        try:
            formattedshotsdict[i]
        except KeyError:
            formattedshotsdict[i] = {}
        formattedshotsdict[i][key] = shotsdict[key][i]

formattedjsonstring = json.dumps(formattedshotsdict, indent=4)
with open('formattedshots.json', 'w') as f:
    f.write(formattedjsonstring)

team_shots = shots[shots['team'] == team]

xs = []
ys = []
for loc in team_shots.get('location', []):
    if isinstance(loc, (list, tuple)) and len(loc) >= 2:
        xs.append(loc[0])
        ys.append(loc[1])

xsgoals = []
ysgoals = []

xsnon_goals = []
ysnon_goals = []

print(xs)
print(xsgoals)
print(xsnon_goals)

for outcome in team_shots.get('shot_outcome', []):
    if outcome == 'Goal':
        xsgoals.append(xs[team_shots.index.get_loc(team_shots[team_shots['shot_outcome'] == outcome].index[0])])
        ysgoals.append(ys[team_shots.index.get_loc(team_shots[team_shots['shot_outcome'] == outcome].index[0])])
    else:
        ysnon_goals.append(ys[team_shots.index.get_loc(team_shots[team_shots['shot_outcome'] == outcome].index[0])])
        xsnon_goals.append(xs[team_shots.index.get_loc(team_shots[team_shots['shot_outcome'] == outcome].index[0])])

pitch = Pitch(pitch_type='statsbomb', line_color='white', pitch_color='grass', line_alpha=0.8)
fig, ax = pitch.draw(figsize=(10, 7))

if xsgoals and ysgoals:
    pitch.scatter(xsgoals, ysgoals, ax=ax, color='white', s=120, edgecolors='black', linewidth=0.8, zorder=3)
if xsnon_goals and ysnon_goals:
    pitch.scatter(xsnon_goals, ysnon_goals, ax=ax, color='red', s=120, edgecolors='black', linewidth=0.8, zorder=3)

fig.savefig('pitch.png', dpi=300, bbox_inches='tight')
plt.show()

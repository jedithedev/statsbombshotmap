from statsbombpy import sb
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import json

shots = None

pitch = Pitch(pitch_type='statsbomb', line_color='white', pitch_color='grass', line_alpha=0.8)
fig, ax = pitch.draw(figsize=(10, 7))

def mapShots(team, ha): 
    team_shots = shots[shots['team'] == team]

    xs = []
    ys = []
    xg_vals = []
    # iterate rows so location and xg stay aligned
    for _, row in team_shots.iterrows():
        loc = row.get('location', None)
        if isinstance(loc, (list, tuple)) and len(loc) >= 2:
            x = (120 - loc[0]) if ha else loc[0]
            y = loc[1]
            xs.append(x)
            ys.append(y)
        else:
            xs.append(None)
            ys.append(None)

        # robust xG extraction from common possible fields
        xg = row.get('shot_statsbomb_xg')
        if xg is None:
            shotdict = row.get('shot') if isinstance(row.get('shot'), dict) else {}
            xg = shotdict.get('statsbomb_xg') if isinstance(shotdict, dict) else None
        if xg is None:
            xg = row.get('shot_xg')  # possible alternative name
        try:
            xg_val = float(xg) if xg is not None else 0.0
        except Exception:
            xg_val = 0.0
        xg_vals.append(xg_val)

    xsgoals = []
    ysgoals = []
    sizes_goals = []
    xsnon_goals = []
    ysnon_goals = []
    sizes_non_goals = []

    for idx, outcome in enumerate(team_shots.get('shot_outcome', [])):
        x = xs[idx]
        y = ys[idx]
        if x is None or y is None:
            continue
        name = outcome.get('name') if isinstance(outcome, dict) else outcome
        # size scaling: base + xg * scale
        size = 120 + xg_vals[idx] * 1000
        if name == 'Goal':
            xsgoals.append(x)
            ysgoals.append(y)
            sizes_goals.append(size)
        else:
            xsnon_goals.append(x)
            ysnon_goals.append(y)
            sizes_non_goals.append(size)

    goals_count = len(xsgoals)
    total_shots = len([x for x in xs if x is not None])
    print(f"total shots: {total_shots}  goals: {goals_count}  non-goals: {len(xsnon_goals)}")

    if xsgoals and ysgoals:
        pitch.scatter(xsgoals, ysgoals, ax=ax, color='white' if ha else 'green',
                      s=sizes_goals, edgecolors='black', linewidth=0.8, zorder=3)
    if xsnon_goals and ysnon_goals:
        pitch.scatter(xsnon_goals, ysnon_goals, ax=ax, color='red' if ha else 'pink',
                      s=sizes_non_goals, edgecolors='black', linewidth=0.8, zorder=3)

    label_text = f"{team} : {total_shots} ({goals_count})"
    if ha:
        ax.text(0.03, 0.97, label_text, transform=ax.transAxes, ha='left', va='top',
                fontsize=14, fontweight='bold', color='white', bbox=dict(facecolor='black', alpha=0.6, pad=4))
    else:
        ax.text(0.97, 0.97, label_text, transform=ax.transAxes, ha='right', va='top',
                fontsize=14, fontweight='bold', color='white', bbox=dict(facecolor='black', alpha=0.6, pad=4))

def drawShots(match_id):
    global shots
    #team = 'Schalke 04'


    lineups = sb.lineups(match_id=match_id)

    print(lineups.keys())

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

    # 120 by 80



    mapShots(list(lineups.keys())[0], True)
    mapShots(list(lineups.keys())[1], False)


    fig.savefig('pitch.png', dpi=300, bbox_inches='tight')

    plt.show()    

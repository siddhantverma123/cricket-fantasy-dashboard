import streamlit as st
import requests
import pandas as pd

# -------------------------
# API KEY
# -------------------------
API_KEY = "28ec5cc1-5e9f-47c1-aabb-355e71cde094"

st.set_page_config(page_title="🏏 Live Fantasy Cricket", layout="wide")

st.title("🏏 LIVE Cricket Fantasy Dashboard")
st.markdown("Real-time scores + Fantasy points | Powered by CricAPI")

# -------------------------
# GET LIVE MATCHES
# -------------------------
@st.cache_data(ttl=60)
def get_matches():

    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

    try:
        r = requests.get(url)
        data = r.json()
        return data.get("data", [])
    except:
        return []

matches = get_matches()

match_id = None

if matches:

    match_names = [
        f"{m['team1']} vs {m['team2']}"
        for m in matches[:10]
    ]

    selected = st.selectbox(
        "Select Match",
        range(len(match_names)),
        format_func=lambda x: match_names[x]
    )

    match = matches[selected]

    st.subheader(match_names[selected])
    st.info(match.get("status","Live"))

    match_id = match.get("id")

else:

    st.warning("No live matches found or API limit reached")

# -------------------------
# GET PLAYERS
# -------------------------
@st.cache_data(ttl=60)
def get_players(match_id):

    if not match_id:
        return []

    url = f"https://api.cricapi.com/v1/match_squad?apikey={API_KEY}&id={match_id}"

    try:
        r = requests.get(url)
        data = r.json()

        players = []

        for team in data.get("data",[]):

            for p in team.get("players",[]):

                players.append({
                    "Player": p.get("name"),
                    "Runs":0,
                    "Fours":0,
                    "Sixes":0,
                    "Wickets":0,
                    "Catches":0,
                    "Runouts":0,
                    "Stumpings":0,
                    "Maidens":0,
                    "HatTrick":0,
                    "Duck":0
                })

        return players

    except:
        return []

players = get_players(match_id)

# -------------------------
# FANTASY POINTS
# -------------------------
def fantasy_points(player):

    runs = player.get("Runs",0)
    fours = player.get("Fours",0)
    sixes = player.get("Sixes",0)
    wickets = player.get("Wickets",0)
    catches = player.get("Catches",0)
    runouts = player.get("Runouts",0)
    stumpings = player.get("Stumpings",0)
    maidens = player.get("Maidens",0)
    hat_trick = player.get("HatTrick",0)
    duck = player.get("Duck",0)

    points = 0

    # Batting
    points += runs

    if runs >= 100:
        points += 50
    elif runs >= 80:
        points += 40
    elif runs >= 50:
        points += 30
    elif runs >= 30:
        points += 20

    if duck:
        points -= 10

    # Bowling
    if wickets == 1:
        points += 30
    elif wickets == 2:
        points += 80
    elif wickets == 3:
        points += 120
    elif wickets == 4:
        points += 160
    elif wickets >= 5:
        points += 200

    # Fielding
    points += catches * 10
    points += runouts * 10
    points += stumpings * 10

    # Special
    points += maidens * 100

    if hat_trick:
        points += 300

    return points

# -------------------------
# CREATE TABLE
# -------------------------
fantasy_table = []

for p in players:

    pts = fantasy_points(p)

    fantasy_table.append({
        **p,
        "Total Points": pts
    })

fantasy_df = pd.DataFrame(fantasy_table)

# -------------------------
# ERROR SAFE CHECK
# -------------------------
if fantasy_df.empty:

    st.warning("No player data available")

else:

    fantasy_df = fantasy_df.sort_values(
        "Total Points",
        ascending=False
    )

    st.markdown("### 🏆 Fantasy Leaderboard")

    st.dataframe(
        fantasy_df,
        use_container_width=True
    )
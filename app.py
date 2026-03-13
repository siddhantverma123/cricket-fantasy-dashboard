import streamlit as st
import requests
import pandas as pd

API_KEY = "28ec5cc1-5e9f-47c1-aabb-355e71cde094"

st.set_page_config(page_title="Cricket Fantasy Analyzer", layout="wide")

st.title("🏏 Cricket Match Fantasy Analyzer")

# -----------------------------
# SEARCH MATCHES
# -----------------------------
@st.cache_data(ttl=60)
def get_matches():

    url = f"https://api.cricapi.com/v1/cricScore?apikey={API_KEY}"

    try:
        r = requests.get(url)
        data = r.json()
        return data.get("data",[])
    except:
        return []

matches = get_matches()

# Search bar
search = st.text_input("🔎 Search match (Team name)")

filtered_matches = []

if matches:
    for m in matches:
        name = f"{m['t1']} vs {m['t2']}"
        if search.lower() in name.lower():
            filtered_matches.append(m)

# -----------------------------
# MATCH SELECT
# -----------------------------
match_id = None

if filtered_matches:

    match_names = [
        f"{m['t1']} vs {m['t2']}" for m in filtered_matches
    ]

    selected = st.selectbox(
        "Select Match",
        range(len(match_names)),
        format_func=lambda x: match_names[x]
    )

    match = filtered_matches[selected]

    st.subheader(match_names[selected])
    st.info(match.get("status"))

    match_id = match.get("id")

else:
    st.warning("No matches found")

# -----------------------------
# GET PLAYERS
# -----------------------------
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
                    "Player":p.get("name"),
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

# -----------------------------
# FANTASY POINTS
# -----------------------------
def fantasy_points(p):

    runs = p.get("Runs",0)
    fours = p.get("Fours",0)
    sixes = p.get("Sixes",0)
    wickets = p.get("Wickets",0)
    catches = p.get("Catches",0)
    runouts = p.get("Runouts",0)
    stumpings = p.get("Stumpings",0)
    maidens = p.get("Maidens",0)
    hat = p.get("HatTrick",0)
    duck = p.get("Duck",0)

    points = 0

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

    points += catches*10
    points += runouts*10
    points += stumpings*10

    points += maidens*100

    if hat:
        points += 300

    return points


# -----------------------------
# CALCULATE TEAM TABLE
# -----------------------------
fantasy_table = []

for p in players:

    pts = fantasy_points(p)

    fantasy_table.append({
        **p,
        "Total Points":pts
    })

fantasy_df = pd.DataFrame(fantasy_table)

# -----------------------------
# PLAYER SEARCH
# -----------------------------
st.markdown("### 🔎 Search Player")

player_search = st.text_input("Type player name")

if not fantasy_df.empty:

    filtered_players = fantasy_df[
        fantasy_df["Player"].str.contains(
            player_search,
            case=False
        )
    ]

    if not filtered_players.empty:

        player = filtered_players.iloc[0]

        st.metric(
            label=player["Player"],
            value=f"{player['Total Points']} Fantasy Points"
        )

# -----------------------------
# TEAM FANTASY TABLE
# -----------------------------
st.markdown("### 🏆 Full Team Fantasy Table")

if not fantasy_df.empty:

    fantasy_df = fantasy_df.sort_values(
        "Total Points",
        ascending=False
    )

    st.dataframe(
        fantasy_df,
        use_container_width=True
    )

else:

    st.warning("Player data not available")
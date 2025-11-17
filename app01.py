# app.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
SAVE_FILE = "sports_tournament_dataset.csv"

SPORT_RULES = {
    "Kabaddi": {"players": 7, "subs": 5},
    "Kho-Kho": {"players": 9, "subs": 3},
    "Basketball": {"players": 5, "subs": 7},
    "Volleyball": {"players": 6, "subs": 4},
}

CSV_COLUMNS = [
    "Timestamp", "Game", "Team", "Players", "Substitutes",
    "Played", "Won", "Lost", "Draw", "Goals_For",
    "Goals_Against", "Points"
]

# -----------------------------
# UTILITIES
# -----------------------------
def ensure_csv_exists():
    if not os.path.exists(SAVE_FILE):
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(SAVE_FILE, index=False)

def load_all_teams():
    ensure_csv_exists()

    try:
        df = pd.read_csv(SAVE_FILE)

        # Add missing columns if needed
        for col in CSV_COLUMNS:
            if col not in df.columns:
                df[col] = 0

        return df

    except:
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(SAVE_FILE, index=False)
        return df

def append_team_to_csv(game, team_name, players_list, subs_list):
    ensure_csv_exists()

    new_row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Game": game,
        "Team": team_name.strip(),
        "Players": ", ".join(players_list),
        "Substitutes": ", ".join(subs_list),
        "Played": 0,
        "Won": 0,
        "Lost": 0,
        "Draw": 0,
        "Goals_For": 0,
        "Goals_Against": 0,
        "Points": 0
    }

    df = load_all_teams()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(SAVE_FILE, index=False)

def validate_names(names, expected_count):
    return len(names) == expected_count and all(n.strip() != "" for n in names)

# -----------------------------
# UPDATE MATCH FUNCTION
# -----------------------------
def update_match(game, team, gf, ga):
    df = load_all_teams()

    # Get team row
    row = df[(df["Game"] == game) & (df["Team"] == team)].index

    if len(row) == 0:
        return "❌ Team not found"

    row = row[0]

    # Update goals
    df.loc[row, "Goals_For"] += gf
    df.loc[row, "Goals_Against"] += ga

    # Update played
    df.loc[row, "Played"] += 1

    # Determine Win / Loss / Draw
    if gf > ga:
        df.loc[row, "Won"] += 1
        df.loc[row, "Points"] += 3
    elif gf < ga:
        df.loc[row, "Lost"] += 1
    else:
        df.loc[row, "Draw"] += 1
        df.loc[row, "Points"] += 1

    df.to_csv(SAVE_FILE, index=False)
    return "✅ Match updated successfully!"

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Tournament App", page_icon="🏆", layout="centered")
st.title("🏆 Sports Tournament App")

menu = st.sidebar.radio("Navigation", ["Register Teams", "View All Teams", "Update Match Score"])

# -----------------------------------------------------------
# 1️⃣ REGISTER TEAMS
# -----------------------------------------------------------
if menu == "Register Teams":

    game = st.selectbox("Select Sport/Game", list(SPORT_RULES.keys()))

    players_required = SPORT_RULES[game]["players"]
    subs_required = SPORT_RULES[game]["subs"]

    st.info(f"Rules for {game}: {players_required} Players + {subs_required} Substitutes")

    st.subheader("Team Registration")
    team_name = st.text_input("Team Name")

    players = [st.text_input(f"Player {i+1}") for i in range(players_required)]
    subs = [st.text_input(f"Substitute {i+1}") for i in range(subs_required)]

    if st.button("Save Team"):
        if team_name.strip() == "":
            st.error("Team name cannot be empty.")
        elif not validate_names(players, players_required):
            st.error("Please fill all player names!")
        elif not validate_names(subs, subs_required):
            st.error("Please fill all substitute names!")
        else:
            append_team_to_csv(game, team_name, players, subs)
            st.success(f"Team '{team_name}' saved successfully!")
            st.experimental_rerun()

    st.subheader(f"All Teams in {game}")
    df = load_all_teams()
    st.dataframe(df[df["Game"] == game])

# -----------------------------------------------------------
# 2️⃣ VIEW ALL TEAMS
# -----------------------------------------------------------
if menu == "View All Teams":

    df = load_all_teams()

    if df.empty:
        st.info("No teams registered yet.")
    else:
        st.subheader("All Registered Teams")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Teams CSV", csv, "sports_tournament_dataset.csv")

# -----------------------------------------------------------
# 3️⃣ UPDATE MATCH SCORE
# -----------------------------------------------------------
if menu == "Update Match Score":

    df = load_all_teams()

    game = st.selectbox("Select Game", df["Game"].unique())

    teams = df[df["Game"] == game]["Team"].unique()
    team = st.selectbox("Select Team", teams)

    st.subheader("Enter Match Score")

    gf = st.number_input("Goals For", min_value=0, step=1)
    ga = st.number_input("Goals Against", min_value=0, step=1)

    if st.button("Update Score"):
        msg = update_match(game, team, gf, ga)
        st.success(msg)

    st.subheader("Updated Table")
    st.dataframe(df[df["Game"] == game].sort_values(by="Points", ascending=False))


st.caption("🏆 Tournament App • Team Registration + Match Updating")

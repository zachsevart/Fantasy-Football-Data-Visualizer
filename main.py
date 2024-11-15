import streamlit as st
import pandas as pd
import nfl_data_py as nfl

st.title("Current NFL Fantasy Football Statistics")
st.markdown("""View the stats of every offensive player in the NFL""")

# Sidebar inputs
st.sidebar.header("User Input Features")
selected_year = st.sidebar.selectbox("Year", list(reversed(range(2005, 2025))))

@st.cache_data
def load_data(year):
    url = f"https://fantasydata.com/nfl/fantasy-football-leaders?scope=season&sp={year}_REG&scoring=fpts_ppr&order_by=fpts_ppr&sort_dir=desc"
    html = pd.read_html(url, header=1)
    df = html[0]
    df.rename(columns={'YDS.1': 'Rushing Yards', 'YDS.2': 'Receiving Yards', 'TD.1': 'Rushing TDs', 'TD.2': 'Receiving TDs'}, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df.fillna(0)

# Function to get game log for the selected player
def game_log(year, name):
    weeklySum = nfl.import_weekly_data(
        [year],
        ['week', 'player_display_name', 'headshot_url', 
         'fantasy_points', 'receiving_yards', 'receptions', 'receiving_tds', 
         'position', 'target_share', 'air_yards_share']
    )
    # Filter by player name
    playerdf = weeklySum[weeklySum["player_display_name"] == name]

    # Extract the headshot URL
    headshot_url = None
    if not playerdf.empty and "headshot_url" in playerdf.columns:
        headshot_url = playerdf.iloc[0]["headshot_url"]
        # Drop the headshot_url column to clean up the DataFrame
        playerdf = playerdf.drop(columns=["headshot_url", "player_display_name"])
    
    return playerdf, headshot_url

    

# Clear Cache and Session State Buttons
if st.sidebar.button("Clear Cache"):
    st.cache_data.clear()
if st.sidebar.button("Clear Session State"):
    st.session_state.clear()

# Load main data
playerStats = load_data(selected_year)

# Sidebar filters
teams = sorted(playerStats.TEAM.unique())
selected_teams = st.sidebar.multiselect("Team", teams, teams)
positions = ["RB", "QB", "WR", "FB", "TE"]
selected_positions = st.sidebar.multiselect("Position", positions, positions)

# Filtered data
df_select = playerStats[(playerStats.TEAM.isin(selected_teams)) & (playerStats.POS.isin(selected_positions))]
st.header("Display player stats of selected teams")
st.dataframe(df_select)



# Header
st.header("Game log")

# Dropdown to select player
players = sorted(playerStats.NAME.unique())  # Assuming playerStats is a valid DataFrame
playerGameLog = st.selectbox("Players", players)  # Select one player
scoringStyle = st.selectbox("Scoring Style", ['No PPR', 'Half PPR', 'PPR'])





# Fetch game log data dynamically
if playerGameLog:  # Ensure a player is selected



    fork, headshot_url = game_log(selected_year, playerGameLog)  # Use selected player
    if scoringStyle == "Half PPR":
        fork["fantasy_points"] += fork["receptions"] * 0.5

    elif scoringStyle == "PPR":
        fork["fantasy_points"] += fork["receptions"]

    # Create a two-column layout
    col1, col2 = st.columns([1, 4])  # Adjust the width ratio as needed

    # Display the player's headshot in the left column
    with col1:
        if headshot_url:
            st.image(
                headshot_url,
                caption=f"{playerGameLog}",
                width=150  # Set the width to make the image smaller
            )
        else:
            st.write("No headshot available.")

    # Apply conditional formatting to the 'fantasy_points' column
    def highlight_points(val):
        """Set background color based on fantasy_points."""
        if val < 10:
            return 'background-color: red; color: white; opacity: 0.7;'
        elif 10 <= val <= 14:
            return 'background-color: yellow; color: black; opacity: 0.7;'
        elif 14 < val <= 24:
            return 'background-color: green; color: white; opacity: 0.7;'
        elif 24 < val <= 35:
            return 'background-color: violet; color: blue; opacity: 0.8;'
        else:
            return 'background-color: gold; color: brown; opacity: 0.9;'

    # Apply formatting to the DataFrame
    if not fork.empty:
        styled_fork = fork.style.applymap(
            highlight_points, subset=['fantasy_points']
        )

        # Convert styled DataFrame to HTML and display using markdown
        with col2:
            st.markdown(
                styled_fork.to_html(escape=False, index=False), unsafe_allow_html=True
            )




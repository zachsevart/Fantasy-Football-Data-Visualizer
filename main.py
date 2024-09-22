import pandas as pd
import requests
import streamlit as st


season_id = "2024"

url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{}/players?scoringPeriodId=0&view=players_wl".format(season_id)

teamUrl = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{}?view=proTeamSchedules_wl".format(season_id)

league_id = "726244831"

espn_cookies = {"swid" : "{9B378FA4-FF7E-4A2E-9642-5BD40FA9792F}", "espn_s2" : "AECnQvlROrsEi9zJjkWEELp2Bf0pPwrHh/eSuOtiLzr33NBA50nx71JbZpUAoeH3RDxVyKri5IiEVkl7PicQApwvmVzKGeBrJBBh7CCwFOkCpEKdhVYDAKNvWICcmAiNikwma9KXhkxlBvpJe2npIlDVdHHt0zu4Ccnjv4rhroCVndy0bUOsXdNOQGfoXVF4HkMqLtd6kmHptSNAZHO/lTj/G14qarL+0ydl1VW67w5JI494t2aNhwARE0Zjrcko23YiEJmi6R4+lOTarHdONWePAPEEFJ58IO2xv9GTGfLrNy8uCN94K1iQjrWtGn01D/c="}

headers = {
    'Connection' : 'keep-alive',
    'Accept' : 'application/json, test/plain, */*',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
    'x-fantasy-filter' : '{"filterActive":null}',
    'x-fantasy-platform' : 'kona-PROD-924d3c065ac5086e75ca68478d4e78341e18ba53',
    'x-fantasy-source' : 'kona'
}



pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)



def get_draft_details(league_id, season_id):

    url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{}/segments/0/leagues/{}?view=mDraftDetail&view=mSettings&view=mTeam&view=modular&view=mNav".format(season_id, league_id)

    r = requests.get(url, headers=headers, cookies = espn_cookies)

    raw = r.json()
    draftDetails = raw[0]
    picks = draftDetails['draftDetail']['picks']
    df = pd.DataFrame(picks)
    draft_df = df[['overallPickNumber', 'playerId', 'teamId']].copy()
    return draft_df

def get_player_info(season_id):
    url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{}/players?scoringPeriodId=0&view=players_wl".format(season_id)

    r = requests.get(url, headers=headers, cookies = espn_cookies)

    raw = r.json()
    players = raw[0]

    df = pd.DataFrame(players)


    player_df = df[['defaultPositionId', 'fullName', 'id', 'proTeamId']].copy()
    player_df.rename(columns= {'id':'player_id'}, inplace = True)

    return player_df

def get_team_info(season_id):
    url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{}?view=proTeamSchedules_wl".format(season_id)

    r = requests.get(url, headers=headers, cookies = espn_cookies)

    raw = r.json()

    team_names = raw['settings']['proTeams']

    dfteam = pd.DataFrame(team_names)
    teamdf = dfteam[['id', 'location', 'name']].copy()
    teamdf["team name"] = teamdf['location'].astype(str) + ' '+ teamdf['name']
    teamdf.rename(columns = {'id': 'team_id'}, inplace = True)



st.title("Fantasy Football Data Viewer")

# Inputs for league_id and season_id
league_id_input = st.text_input("Enter League ID", value=league_id)
season_id_input = st.text_input("Enter Season ID", value=season_id)

# Select which data to view
option = st.selectbox(
    'Which data would you like to view?',
    ('Draft Details', 'Player Info', 'Team Info')
)

if st.button("Fetch Data"):
    if option == 'Draft Details':
        draft_data = get_draft_details(league_id_input, season_id_input)
        st.write("Draft Details Data")
        st.dataframe(draft_data)
    elif option == 'Player Info':
        player_data = get_player_info(season_id_input)
        st.write("Player Info Data")
        st.dataframe(player_data)
    elif option == 'Team Info':
        team_data = get_team_info(season_id_input)
        st.write("Team Info Data")
        st.dataframe(team_data)













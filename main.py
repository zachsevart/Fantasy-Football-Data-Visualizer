import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import pandas as pd



st.title('Current Wide Reciever stats')

st.markdown("""filler text""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(2005,2025))))

@st.cache_data
def load_data(year):
    url = "https://fantasydata.com/nfl/fantasy-football-leaders?scope=season&sp={}_REG&scoring=fpts_ppr&order_by=fpts_ppr&sort_dir=desc".format(year)
    html = pd.read_html(url, header = 1)
    df = html[0]
    print(df.columns)
    df.rename(columns={'YDS.1': 'Rushing Yards', 'YDS.2' : 'Receiving Yards ', 'TD.1': 'Rushing TDs', 'TD.2': 'Receiving TDs'}, inplace=True)
    df.reset_index(drop=True, inplace=True)
    raw = df
    raw = raw.fillna(0)

    
    
    return raw

def game_log(year, name):
    url = "https://fantasydata.com/nfl/{}-fantasy/20868?scoring=fpts_ppr&sp={}_REG".format(name, year)
    html = pd.read_html(url, header = 1)
    df = html[2]
    print(df.columns)
    raw = df
    raw = raw.fillna(0)

    return raw

fork = game_log(selected_year, 'alexander-mattison')

playerStats = load_data(selected_year)

teams = sorted(playerStats.TEAM.unique())
selected = st.sidebar.multiselect('Team', teams, teams)

positions = ['RB', 'QB', 'WR', 'FB', 'TE']
selected_pos = st.sidebar.multiselect('Position', positions, positions)

df_select = playerStats[(playerStats.TEAM.isin(selected)) & (playerStats.POS.isin(selected_pos))]

st.header('Display player stats of selected teams')
st.write('Data dimension: ' + str(df_select.shape[0]) + ' rows and ' + str(df_select.shape[1]) + ' columns.')
st.dataframe(df_select)
st.dataframe(fork)

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
         ]
    )
    # Filter by player name
    playerdf = weeklySum[weeklySum["player_display_name"] == name]

    # Extract the headshot URL
    headshot_url = None
    if not playerdf.empty and "headshot_url" in playerdf.columns:
        headshot_url = playerdf.iloc[0]["headshot_url"]
        # Drop the headshot_url column to clean up the DataFrame
        playerdf = playerdf.drop(columns=["headshot_url", "player_display_name"])
    
    playerdf.rename(columns={'receiving_yards': 'Receiving Yards', 'fantasy_points': 'Fantasy Points', 'receptions': 'Receptions', 'receiving_tds': 'Receiving TDs'}, inplace=True)

    
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
        fork["Fantasy Points"] += fork["Receptions"] * 0.5

    elif scoringStyle == "PPR":
        fork["Fantasy Points"] += fork["Receptions"]

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
            highlight_points, subset=['Fantasy Points']
        )

        # Convert styled DataFrame to HTML and display using markdown
        with col2:
            st.markdown(
                styled_fork.to_html(escape=False, index=False), unsafe_allow_html=True
            )


from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch


st.title("NFL Data Question Answering")
print(column for column in nfl.see_weekly_cols())
# Load NFL weekly data
nfl_data = nfl.import_weekly_data([2024])

# Preprocess the data
relevant_columns = ['player_name', 'week', 'receiving_yards', 'receiving_tds','passing_tds', 'passing_yards','recent_team', 'position', 'fantasy_points_ppr']
nfl_data = nfl_data[relevant_columns]
nfl_data = nfl_data.fillna(0)
nfl_text = nfl_data.to_string(index=False)

# Split the data into chunks
def split_text(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

chunks = split_text(nfl_text)

# Load the embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Embed the chunks
with st.spinner('Indexing data...'):
    chunk_embeddings = embedder.encode(chunks, convert_to_tensor=True)

# Load the QA pipeline
qa_pipeline = pipeline(
    "question-answering",
    model="deepset/roberta-base-squad2",
    tokenizer="deepset/roberta-base-squad2"
)

# Instructions to the user
st.write("""
    **Instructions:**
    - Ask questions about NFL data, such as:
        - "Who has the most receiving yards?"
        - "Which player scored the most passing touchdowns?"
    - The model will provide answers based on the available data.
""")

# User input
user_question = st.text_input("Ask a question about NFL data:")

if user_question:
    with st.spinner('Processing your question...'):
        # Embed the user's question
        question_embedding = embedder.encode(user_question, convert_to_tensor=True)

        # Compute cosine similarities
        cosine_scores = util.cos_sim(question_embedding, chunk_embeddings)[0]

        # Find the most relevant chunks
        top_k = 3
        top_results = torch.topk(cosine_scores, k=top_k)

        # Combine the top chunks
        relevant_text = ' '.join([chunks[idx] for idx in top_results.indices])

        # Ensure context length is within model limits
        max_context_length = 450  # Adjusted to fit within model's token limit
        tokens = qa_pipeline.tokenizer.tokenize(relevant_text)
        if len(tokens) > max_context_length:
            tokens = tokens[:max_context_length]
            relevant_text = qa_pipeline.tokenizer.convert_tokens_to_string(tokens)

        # Get the answer
        result = qa_pipeline({'context': relevant_text, 'question': user_question})
        st.write(f"**Answer:** {result['answer']}")



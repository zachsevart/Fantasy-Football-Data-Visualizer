from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from pydataset import data
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import nfl_data_py as nfl

print(nfl.see_weekly_cols())
#print(nfl.import_team_desc())
weeklySum = nfl.import_weekly_data([2024], ['week','player_id','player_display_name','headshot_url', 'fantasy_points', 'receiving_yards','receptions', 'receiving_tds', 'position', 'target_share', 'air_yards_share'])
weeklySum['fantasy_points'] += weeklySum['receptions']
wrSum = weeklySum[(weeklySum["position"] == "WR") & (weeklySum["player_display_name"] == "CeeDee Lamb")]

wrSum['cumulative_yards'] = wrSum['receiving_yards'].cumsum().shift(1)
wrSum['cumulative_receptions'] = wrSum['receptions'].cumsum().shift(1)
wrSum['cumulative_tds'] = wrSum['receiving_tds'].cumsum().shift(1)

wrSum['average_yards'] = wrSum['cumulative_yards'] / (wrSum['week'] - 1)
wrSum['average_receptions'] = wrSum['cumulative_receptions'] / (wrSum['week'] - 1)
wrSum['average_tds'] = wrSum['cumulative_tds'] / (wrSum['week'] - 1)

# Replace NaN values in the first row (created by shift) with 0
wrSum.fillna(0, inplace=True)

print(wrSum.head())


# Define features (X) and targets (y)
X = wrSum[['cumulative_yards', 'cumulative_receptions', 'cumulative_tds',
           'average_yards', 'average_receptions', 'average_tds']]
y = wrSum[['receiving_yards', 'receptions', 'receiving_tds']]



# Sequential train-test split (80% training, 20% testing)
# Sequential train-test split (80% training, 20% testing)
train_size = int(len(wrSum) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]



model = MultiOutputRegressor(RandomForestRegressor(random_state=42))
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Convert predictions to DataFrame
predictions = pd.DataFrame(y_pred, columns=['predicted_yards', 'predicted_receptions', 'predicted_tds'])


mse_yards = mean_squared_error(y_test['receiving_yards'], y_pred[:, 0])
mse_receptions = mean_squared_error(y_test['receptions'], y_pred[:, 1])
mse_tds = mean_squared_error(y_test['receiving_tds'], y_pred[:, 2])

print(f"MSE for Yards: {mse_yards:.2f}")
print(f"MSE for Receptions: {mse_receptions:.2f}")
print(f"MSE for TDs: {mse_tds:.2f}")

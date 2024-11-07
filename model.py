from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from pydataset import data
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import nfl_data_py as nfl

print(nfl.see_weekly_cols())
#print(nfl.import_team_desc())
weeklySum = nfl.import_weekly_data([2024], ['player_id','player_name', 'fantasy_points', 'target_share', 'position'])
wrSum = weeklySum[(weeklySum["position"] == "WR")]
print(wrSum)



import pandas as pd
import numpy as np
from pathlib import Path
import bus_optmizer_ajmanv0_3_4 as bo3
PARENT_DIR = Path(__file__).resolve().parent

# Go up one folder to project root, then down into data/passengers.csv
csv_path = PARENT_DIR.parent / "data" / "passengers.csv"

# Load data safely
df = pd.read_csv(str(csv_path))

X = bo3.X1
# t1 is passenger_demand
# t2 is capacity_limit
# t3 is traffic_delay_mins
# t means target (in general)
t1 = bo3.y1
t2 = bo3.y2
t3 = bo3.y3

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
X1_train, X1_test, y1_train, y1_test = train_test_split(X, t1, test_size=0.2, random_state=42,)

forestmodel = RandomForestRegressor(n_estimators=300, max_depth=20, random_state=42, n_jobs=-1)
xgbmodel = XGBRegressor(n_estimators=300, max_depth=8, learning_rate=0.05, random_state=42, n_jobs=-1)
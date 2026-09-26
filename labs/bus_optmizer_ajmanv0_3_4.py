import pandas as pd
import numpy as np
import os
import contextlib
import sys
from pathlib import Path

# Get the 'nbconvert' folder path
NBCONVERT_DIR = Path(__file__).resolve().parent

# Go up one folder to project root, then down into data/passengers.csv
csv_path = NBCONVERT_DIR.parent / "data" / "passengers.csv"

# Load data safely
df = pd.read_csv(str(csv_path))


def turn_time_values(time_string):
    hours, minutes = map(int, time_string.split(':'))
    return (hours * 60) + minutes





def recommended_bus_freq(route, demand, capacity, delay, is_peak=False):
    ideal_capacity = capacity - 15
    high_pressure = (demand > 90) | (delay>15)
    route = route.lower().strip().replace('route', '').replace('_', '').replace(' ', '').replace('bus','').upper()
    if route == 'AJ3':
        return 15 if high_pressure else 30
    elif route == "AJ2":
        # Options: 20 to 25 mins
        return 20 if high_pressure else 25
        
    elif route == "AJ3":
        # Options: 20 to 30 mins
        return 20 if high_pressure else 30
        
    elif route == "E400":
        # Peak: 15 to 20 mins | Off-Peak: 30 to 45 mins
        if is_peak:
            return 15 if high_pressure else 20
        else:
            return 30 if high_pressure else 45
            
    elif route == "E411":
        # Fixed standard at 30 minutes
        return 20 if high_pressure else 30
        
    else:
        return "Unknown Route"



df['time_mins'] = df['time'].apply(turn_time_values)

demand = np.random.randint(0,101)
area = np.random.choice(df['area'].unique())
time = np.random.choice(df['time'].unique())
route = np.random.choice(df['bus_route'].unique())

X1 = df.drop(columns=['passenger_demand', 'time', 'date', 'capacity_limit', 'traffic_delay_mins'])
X1 = pd.get_dummies(X1, columns=['day', 'area', 'bus_route'], drop_first=True)
y1 = df['passenger_demand']
y2 = df['capacity_limit']
y3 = df['traffic_delay_mins']

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

X1_train, X1_test, y1_train, y1_test = train_test_split(X1, y1, test_size=0.2, random_state=42,)
from xgboost import XGBRegressor

xgbmodel = XGBRegressor(n_estimators=300, max_depth=8, learning_rate=0.05, random_state=42, n_jobs=-1)
xgbmodel.fit(X1_train, y1_train)

import shutil
width = shutil.get_terminal_size().columns

areaa = 'AL RASHIDIYA'
routee = 'E411'
timee = '19:30'
dayy = 'SATURDAY'

def pred(target, input, model=xgbmodel, x=X1, df=df):
    X1_train, X1_test, y1_train, y1_test = train_test_split(x, df[f'{target}'], test_size=0.2, random_state=42,)
    model.fit(X1_train, y1_train)
    return model.predict(input)
# ---- ADDED: "tee" so prints go to console AND file ----
class _Tee:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data):
        for s in self.streams:
            s.write(data)
    def flush(self):
        for s in self.streams:
            s.flush()

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()

output_dir = os.path.abspath(os.path.join(script_dir, '..', 'outputs'))
os.makedirs(output_dir, exist_ok=True)
report_path = os.path.join(output_dir, 'bus_frequency_report.txt')
# ---- END ADDED ----
def report():
# ---- everything below is your ORIGINAL code, just indented one level inside the 'with' ----
    with open(report_path, 'w', encoding='utf-8') as report_file, \
        contextlib.redirect_stdout(_Tee(sys.stdout, report_file)):

        print(f'{'=' * width}')
        print('BUS FREQUENCY REPORT'.center(width))
        print('(bus_optimizer_ajman V0.4)'.center(width))
        print(f'{'=' * width}')
        print(f'''area:{' ' * 5} {areaa}
        Route:{' ' * 5} {routee}
        Time:{' ' * 5} {timee}
        Day:{' ' * 5} {dayy}''')

        tempdf1 = pd.DataFrame(0, index=[0], columns=X1.columns)
        tempdf1[f'area_{areaa.strip().lower()}'] = 1
        tempdf1[f'bus_route_route {routee.lower().strip().replace('route', '').replace('_', '').replace(' ', '').replace('bus','').upper()}'] = 1
        tempdf1[f'time_mins'] = turn_time_values(timee)
        tempdf1[f'day_{dayy.strip().capitalize()}'] = 1

        capacity = 50
        predicted_demand = pred('passenger_demand', tempdf1)[0]
        predicted_delay = pred('traffic_delay_mins', tempdf1)[0]
        recommended_bus_loads = ((predicted_demand // capacity) + 1)

        print(f'\npredicted passenger demand: {predicted_demand:.0f}')
        print(f'predicted traffic delay (in mins): {predicted_delay:.0f}')
        print(f'Bus capacity:{' ' * 5} {capacity}\n')
        print(f'{'-' * width}')

        print('RECOMMENDATION')
        print(f'{'-' * width}\n')
        print(f'HIGH DEMAND:{' ' * 5} {'TRUE' if (predicted_demand > 90) or (predicted_delay>15) else 'FALSE'}')
        print('Reason:')
        print(f"Based off historical data, AI predicts that transportation in {areaa} going on route {routee} at {timee} is usually {'busy' if (predicted_demand > 90) or (predicted_delay>15) else 'quite'}\n")
        print(f'Recommended frequency:{' ' * 5} every {recommended_bus_freq('E411', predicted_demand, 50, predicted_delay)} minutes')
        print('Reason:')
        print(f'{'Commuter dissatisfaction rises when service frequency cannot accommodate high passenger volume' if (predicted_demand > 90) or (predicted_delay>15) else 'too much buses with low demand leads to fuel waste and inefficiency'}\n')
        print(f'Recommended bus loads:{' ' * 5} {recommended_bus_loads:.0f}')
        print('Reason:')
        print(f'With a predicted demand of {predicted_demand:.0f}, and a capacity of {capacity:.0f}, {recommended_bus_loads:.0f} bus {'loads' if recommended_bus_loads > 1 else 'load'} is more than sufficient, providing an additional {((capacity * recommended_bus_loads) - predicted_demand):.0f} {'seat' if ((capacity * recommended_bus_loads) - predicted_demand) == 1 else 'seats'} in case of AI underestimation or outliers\n')
        print(f'{'-' * width}')

        print('EXPECTED RESULTS')
        print(f'{'-' * width}\n')
        if (predicted_demand > 90) or (predicted_delay>15):
            print('More buses during peak hours:')
            print('-less overcrowding')
            print('-shorter passenger waiting time')
            print('-improved schedule reliabality and on-time preformance')
            print('-higher overall commuter satisfaction')

        elif (predicted_demand <= 90) and (predicted_delay<=15):
            print('Fewer buses during off-peak hours:')
            print('-reduced fuel consumption')
            print('-reduced vehicle emissions')
            print('-extended vehicle maintenance lifespans')
            print('-optimized resource allocations for peak demands')
        print(f'{'=' * width}\n')

    print(f'\nReport saved to: {report_path}')
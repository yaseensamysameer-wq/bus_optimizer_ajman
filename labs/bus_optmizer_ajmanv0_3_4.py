import pandas as pd
import numpy as np
import os
import contextlib
import sys
from pathlib import Path
import streamlit as st

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
        
    elif route == "AJ1":
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
# ---- ADDED: "tee" so st.writes go to console AND file ----
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
def report(time, area, route, day, input, width=80):
    capacity = 50
    predicted_demand = pred('passenger_demand', input)[0]
    predicted_delay = pred('traffic_delay_mins', input)[0]
    
    high_demand = (predicted_demand > 90) or (predicted_delay > 15)
    recommended_bus_loads = (predicted_demand // capacity) + 1
    
    freq = recommended_bus_freq(route, predicted_demand, capacity, predicted_delay)
    extra_seats = (capacity * recommended_bus_loads) - predicted_demand
    seat_word = 'seat' if extra_seats == 1 else 'seats'
    load_word = 'loads' if recommended_bus_loads > 1 else 'load'

    # # ---------- Plain-text version, for the saved report file ----------
    # lines = build_report_lines(  # same content as before, unchanged logic
    #     time, area, route, day, capacity, predicted_demand, predicted_delay,
    #     high_demand, recommended_bus_loads, freq, extra_seats, seat_word,
    #     load_word, width,
    # )
    # with open(report_path, 'w', encoding='utf-8') as report_file, \
    #     contextlib.redirect_stdout(_Tee(sys.stdout, report_file)):
    #     print('\n'.join(lines))
    
    # ---------- Polished on-screen dashboard ----------
    st.markdown(f"### 🚌 Bus Frequency Report")
    st.caption("bus_optimizer_ajman · V0.4")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Area", area)
    c2.metric("Route", route)
    c3.metric("Time", time)
    c4.metric("Day", day)

    st.divider()

    m1, m2, m3 = st.columns(3)
    m1.metric("Predicted Demand", f"{predicted_demand:.0f} pax")
    m2.metric("Predicted Delay", f"{predicted_delay:.0f} min")
    m3.metric("Bus Capacity", f"{capacity}")

    if high_demand:
        st.error(f"⚠️ **HIGH DEMAND** — {area} on route {route} at {time} is usually busy")
    else:
        st.success(f"✅ **NORMAL DEMAND** — {area} on route {route} at {time} is usually quiet")

    st.divider()
    st.markdown("#### Recommendation")

    r1, r2 = st.columns(2)
    with r1:
        st.metric("Recommended Frequency", f"Every {freq} min")
        with st.expander("Why?"):
            st.write(
                "Commuter dissatisfaction rises when service frequency cannot "
                "accommodate high passenger volume." if high_demand else
                "Too many buses with low demand leads to fuel waste and inefficiency."
            )
    with r2:
        st.metric("Recommended Bus Loads", f"{recommended_bus_loads:.0f}")
        with st.expander("Why?"):
            st.write(
                f"With a predicted demand of {predicted_demand:.0f} and a capacity of "
                f"{capacity:.0f}, {recommended_bus_loads:.0f} bus {load_word} is more "
                f"than sufficient — providing an additional {extra_seats:.0f} "
                f"{seat_word} in case of AI underestimation or outliers."
            )

    st.divider()
    st.markdown("#### Expected Results")

    if high_demand:
        st.markdown("**More buses during peak hours:**")
        for item in [
            "Less overcrowding",
            "Shorter passenger waiting time",
            "Improved schedule reliability and on-time performance",
            "Higher overall commuter satisfaction",
        ]:
            st.markdown(f"- {item}")
    else:
        st.markdown("**Fewer buses during off-peak hours:**")
        for item in [
            "Reduced fuel consumption",
            "Reduced vehicle emissions",
            "Extended vehicle maintenance lifespans",
            "Optimized resource allocations for peak demands",
        ]:
            st.markdown(f"- {item}")

    with st.expander("📄 View raw text report"):
        st.write(f'{'=' * width}')
        st.write('BUS FREQUENCY REPORT'.center(width))
        st.write('(bus_optimizer_ajman V0.4)'.center(width))
        st.write(f'{'=' * width}')
        st.write(f'''area:{' ' * 5} {area}
        Route:{' ' * 5} {route}
        Time:{' ' * 5} {time}
        Day:{' ' * 5} {day}''')

        st.write(f'\npredicted passenger demand: {predicted_demand:.0f}')
        st.write(f'predicted traffic delay (in mins): {predicted_delay:.0f}')
        st.write(f'Bus capacity:{' ' * 5} {capacity}\n')
        st.write(f'{'-' * width}')

        st.write('RECOMMENDATION')
        st.write(f'{'-' * width}\n')
        st.write(f'HIGH DEMAND:{' ' * 5} {'TRUE' if (predicted_demand > 90) or (predicted_delay>15) else 'FALSE'}')
        st.write('Reason:')
        st.write(f"Based off historical data, AI predicts that transportation in {area} going on route {route} at {time} is usually {'busy' if (predicted_demand > 90) or (predicted_delay>15) else 'quite'}\n")
        st.write(f'Recommended frequency:{' ' * 5} every {recommended_bus_freq('E411', predicted_demand, 50, predicted_delay)} minutes')
        st.write('Reason:')
        st.write(f'{'Commuter dissatisfaction rises when service frequency cannot accommodate high passenger volume' if (predicted_demand > 90) or (predicted_delay>15) else 'too much buses with low demand leads to fuel waste and inefficiency'}\n')
        st.write(f'Recommended bus loads:{' ' * 5} {recommended_bus_loads:.0f}')
        st.write('Reason:')
        st.write(f'With a predicted demand of {predicted_demand:.0f}, and a capacity of {capacity:.0f}, {recommended_bus_loads:.0f} bus {'loads' if recommended_bus_loads > 1 else 'load'} is more than sufficient, providing an additional {((capacity * recommended_bus_loads) - predicted_demand):.0f} {'seat' if ((capacity * recommended_bus_loads) - predicted_demand) == 1 else 'seats'} in case of AI underestimation or outliers\n')
        st.write(f'{'-' * width}')

        st.write('EXPECTED RESULTS')
        st.write(f'{'-' * width}\n')
        if (predicted_demand > 90) or (predicted_delay>15):
            st.write('More buses during peak hours:')
            st.write('-less overcrowding')
            st.write('-shorter passenger waiting time')
            st.write('-improved schedule reliabality and on-time preformance')
            st.write('-higher overall commuter satisfaction')

        elif (predicted_demand <= 90) and (predicted_delay<=15):
            st.write('Fewer buses during off-peak hours:')
            st.write('-reduced fuel consumption')
            st.write('-reduced vehicle emissions')
            st.write('-extended vehicle maintenance lifespans')
            st.write('-optimized resource allocations for peak demands')
        st.write(f'{'=' * width}\n')

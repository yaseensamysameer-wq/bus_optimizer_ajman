import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os
import sys


st.write("Current folder:", os.getcwd())
st.write("This file:", __file__)
st.write("Files in folder:", os.listdir(os.path.dirname(__file__)))
st.write("Python path:", sys.path)


import bus_optmizer_ajmanv0_3_4 as bo3
# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Ajman Bus Optimizer",
    page_icon="🚌",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================
file_path = Path(__file__).resolve().parent.parent / "data" / "passengers.csv"

@st.cache_data

def load_data(file=file_path):
    df = pd.read_csv(file)

    # Convert date/time if necessary
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


df = load_data()


# =========================================================
# TITLE
# =========================================================

st.title("🚌 Ajman AI Bus-Route & Commuter Demand Optimizer")

st.write(
    """
    Analyze passenger demand across Ajman and generate
    bus-service recommendations based on predicted demand.
    """
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Controls")

selected_area = st.sidebar.selectbox(
    "Select Area",
    sorted(df["area"].unique())
)

selected_route = st.sidebar.selectbox(
    "Select Bus Route",
    sorted(df["bus_route"].unique())
)


# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df[
    (df["area"] == selected_area) &
    (df["bus_route"] == selected_route)
]


# =========================================================
# TOP METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average Demand",
        f"{filtered_df['passenger_demand'].mean():.0f}"
    )

with col2:
    st.metric(
        "Highest Demand",
        f"{filtered_df['passenger_demand'].max():.0f}"
    )

with col3:
    st.metric(
        "Lowest Demand",
        f"{filtered_df['passenger_demand'].min():.0f}"
    )


st.divider()


# =========================================================
# DEMAND BY HOUR
# =========================================================

st.subheader("📈 Passenger Demand by Hour")

hourly_demand = (
    filtered_df
    .groupby("time")["passenger_demand"]
    .mean()
    .reset_index()
)

fig = px.line(
    hourly_demand,
    x="time",
    y="passenger_demand",
    markers=True,
    title=f"Average Demand — {selected_area}"
)

fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Average Passengers"
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# AREA COMPARISON
# =========================================================

st.subheader("📊 Average Demand by Area")

area_demand = (
    df
    .groupby("area")["passenger_demand"]
    .mean()
    .reset_index()
    .sort_values("passenger_demand", ascending=False)
)

fig_area = px.bar(
    area_demand,
    x="area",
    y="passenger_demand",
    title="Average Passenger Demand by Area"
)

fig_area.update_layout(
    xaxis_title="Area",
    yaxis_title="Average Passengers"
)

st.plotly_chart(fig_area, use_container_width=True)


# =========================================================
# V0.3 / V0.4 PREDICTION SECTION
# =========================================================

st.divider()

st.header("🤖 Demand Prediction & Bus Recommendation")


selected_time = st.selectbox(
    "Select Time",
    sorted(df["time"].unique())
)
print(selected_time)
print(type(selected_time))
df1 = df
df1['time_mins'] = df1['time'].apply(bo3.turn_time_values)
# ---------------------------------------------------------
# TEMPORARY PREDICTION
# ---------------------------------------------------------
# IMPORTANT:
# This is NOT your final machine-learning model.
# Replace this with your V0.3 model later.

time_data = filtered_df[
    filtered_df["time"] == selected_time
]

selected_day = st.sidebar.selectbox(
    "Select Day",
    df["day"].unique()
)
tempdf1 = pd.DataFrame(0, index=[0], columns=bo3.X1.columns)
tempdf1[f'area_{selected_area.strip().lower()}'] = 1
tempdf1[f'bus_route_route {selected_route.lower().strip().replace('route', '').replace('_', '').replace(' ', '').replace('bus','').upper()}'] = 1
tempdf1[f'time_mins'] = bo3.turn_time_values(selected_time)
tempdf1[f'day_{selected_day.strip().capitalize()}'] = 1 
if 'area_ajman industrial area' in tempdf1.columns:
    tempdf1 = tempdf1.drop(columns=['area_ajman industrial area'])
if 'bus_route_route AJ1' in tempdf1.columns:
    tempdf1 = tempdf1.drop(columns=['bus_route_route AJ1'])

predicted_demand = bo3.pred('passenger_demand', tempdf1)[0]

st.metric(
    "Predicted Passenger Demand",
    f"{predicted_demand:.0f} passengers"
)

# =========================================================
# V0.4 BUS RECOMMENDATION
# =========================================================

st.subheader("🚌 Recommended Bus Frequency")


# Temporary example rules.
# You will improve these later.

if predicted_demand < 30:

    demand_level = "LOW"
    recommended_frequency = 30

elif predicted_demand < 60:

    demand_level = "MEDIUM"
    recommended_frequency = 20

elif predicted_demand < 100:

    demand_level = "HIGH"
    recommended_frequency = 10

else:

    demand_level = "VERY HIGH"
    recommended_frequency = 5


st.write(f"**Demand level:** {demand_level}")

st.metric(
    "Recommended Frequency",
    f"Every {recommended_frequency} minutes"
)


if demand_level == "LOW":

    st.info(
        "Low predicted demand. A lower bus frequency may "
        "reduce unnecessary bus trips."
    )

elif demand_level == "MEDIUM":

    st.info(
        "Moderate predicted demand. Maintain normal service "
        "or make a small frequency adjustment."
    )

elif demand_level == "HIGH":

    st.warning(
        "High predicted demand. Consider increasing bus frequency "
        "to reduce passenger waiting and overcrowding."
    )

else:

    st.error(
        "Very high predicted demand. Consider substantially "
        "increasing bus frequency during this period."
    )


# =========================================================
# DATA TABLE
# =========================================================

with st.expander("View filtered data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
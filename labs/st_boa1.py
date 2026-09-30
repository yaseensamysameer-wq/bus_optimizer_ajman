import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os
import sys
import numpy as np




import bus_optmizer_ajmanv0_3_4 as bo3
develepor_pw = "1504"
if "auth" not in st.session_state:
    st.session_state.auth = False

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
# SIDEBAR
# =========================================================

st.sidebar.header("Navigation")
page = st.sidebar.radio('Choose dashboard', ['Overview', 'Developer Mode'])
if page == 'Overview':


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
    # CONTROLS
    # =========================================================
    cola, colb = st.columns(2)

    with cola:
        selected_area = st.selectbox(
            "Select Area",
            sorted(df["area"].unique())
        )

    with colb:
        selected_route = st.selectbox(
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

    cola1, colb1 = st.columns(2)
    with cola1:
        selected_day = st.selectbox(
            "Select Day",
            df["day"].unique()
        )
    with colb1:
        selected_time = st.selectbox(
            "Select Time",
            sorted(df["time"].unique())
        )

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


    
    tempdf1 = pd.DataFrame(0, index=[0], columns=bo3.X1.columns)
    tempdf1[f'area_{selected_area.strip().lower()}'] = 1
    tempdf1[f'bus_route_route {selected_route.lower().strip().replace('route', '').replace('_', '').replace(' ', '').replace('bus','').upper()}'] = 1
    tempdf1[f'time_mins'] = bo3.turn_time_values(selected_time)
    tempdf1[f'day_{selected_day.strip().capitalize()}'] = 1 
    if 'area_ajman industrial area' in tempdf1.columns:
        tempdf1 = tempdf1.drop(columns=['area_ajman industrial area'])
    if 'bus_route_route AJ1' in tempdf1.columns:
        tempdf1 = tempdf1.drop(columns=['bus_route_route AJ1'])



    st.subheader("🤖 AI Demand Prediction")
    report = st.checkbox('Generate Report')
    run = st.button('Run AI Demand Prediction')
    if run:

        with st.status("🤖 AI is analyzing passenger demand...", expanded=True) as status:

            st.write("🔍 Checking selected route...")
            


            st.write("📊 Analyzing historical demand...")

            # Your actual ML prediction
            predicted_demand = bo3.pred('passenger_demand', tempdf1)[0]

            st.write("🧠 Running demand prediction model...")

            # If you have additional processing here,
            # put it here.


            status.update(
                label="✅ AI analysis complete",
                state="complete",
                expanded=False
            )


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

        # if predicted_demand < 30:

        #     demand_level = "LOW"
        #     recommended_frequency = 30

        # elif predicted_demand < 60:

        #     demand_level = "MEDIUM"
        #     recommended_frequency = 20

        # elif predicted_demand < 100:

        #     demand_level = "HIGH"
        #     recommended_frequency = 10

        # else:

        #     demand_level = "VERY HIGH"
        #     recommended_frequency = 5


        # st.write(f"**Demand level:** {demand_level}")

        # st.metric(
        #     "Recommended Frequency",
        #     f"Every {recommended_frequency} minutes"
        # )

    if report and run:
        with st.status("Generating bus report", expanded=True, state='running') as status1:
            st.write('AI is predicting traffic delay')
            st.write('checking criterions...')
            st.write('recommending frequency...')
            st.write('generating report...')
        status1.update(
            state='running'
        )
        bo3.report(selected_time, selected_area, selected_route, selected_day, tempdf1)
        status1.update(
                label="✅ Bus report generated",
                state="complete",
                expanded=False
            )

        
        # if demand_level == "LOW":

        #     st.info(
        #         "Low predicted demand. A lower bus frequency may "
        #         "reduce unnecessary bus trips."
        #     )

        # elif demand_level == "MEDIUM":

        #     st.info(
        #         "Moderate predicted demand. Maintain normal service "
        #         "or make a small frequency adjustment."
        #     )

        # elif demand_level == "HIGH":

        #     st.warning(
        #         "High predicted demand. Consider increasing bus frequency "
        #         "to reduce passenger waiting and overcrowding."
        #     )

        # else:

        #     st.error(
        #         "Very high predicted demand. Consider substantially "
        #         "increasing bus frequency during this period."
        #     )


    # =========================================================
    # DATA TABLE
    # =========================================================

    with st.expander("View filtered data"):

        st.dataframe(
            filtered_df,
            use_container_width=True
        )
elif page == 'Developer Mode':
    # 2. Check authentication status

    if not st.session_state.auth:
        st.subheader("Develepor Password Required")
        
        entered_password = st.text_input("Enter Password", type="password", key="pwd_input")
        
        if st.button("Login"):
            if entered_password == develepor_pw:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

    else:
        st.header('Developer Mode')
        dtab1, dtab2 = st.tabs(['Information', 'Model Testing'])

        with dtab1:
            with st.expander('view file location'):
                st.write("Current folder:", os.getcwd())
                st.write("This file:", __file__)
                st.write("Files in folder:", os.listdir(os.path.dirname(__file__)))
                st.write("Python path:", sys.path)

            with st.expander('view current session state dictionary'):
                st.write(st.session_state)
        with dtab2:
            model_choise = st.radio("Pick AI model to test", ["XGBoost Regressor", "RandomForest Regressor"])
            if model_choise == "XGBoost Regressor":
                model = bo3.xgbmodelR
            if model_choise == "RandomForest Regressor":
                model = bo3.forestmodelR
            target_choise = st.selectbox('Pick target', ['Passenger Demand', 'Traffic Delay Minutes', 'Capacity Limit'])
            if target_choise == 'Passenger Demand':
                target = bo3.y1
            if target_choise == 'Capacity Limit':
                target = bo3.y2
            if target_choise == 'Traffic Delay Minutes':
                target = bo3.y3
            if st.button('Test model'):
                with st.status("🤖 Testing AI model...", expanded=True) as status2:
                    st.write('Importing Models...')
                    from sklearn.model_selection import train_test_split
                    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
                    if model_choise == "XGBoost Regressor":
                        from xgboost import XGBRegressor
                    if model_choise == "RandomForest Regressor":
                        from sklearn.ensemble import RandomForestRegressor
                    st.write('Training the AI...')
                    X_train, X_test, y_train, y_test = train_test_split(bo3.X1, target, test_size=0.2, random_state=42,)
                    model.fit(X_train, y_train)
                    st.write('Testing the model...')
                    y_pred = model.predict(X_test)
                    st.write('Grading the test...')
                    mae = mean_absolute_error(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    rmse = np.sqrt(mse)
                    r2 = r2_score(y_test, y_pred)

                    status2.update(
                        label="✅ AI testing complete",
                        state="complete",
                        expanded=False
                    )
                with st.container(border=True):
                    st.header(f'{model_choise} Test Results')
                    st.write(f'Target: {target_choise}')
                    st.write(f'''
Mean Absolute Error: {mae:.3f}\n
Mean Squared Error: {mse:.3f}\n
Root Mean Squared Error: {rmse:.3f}\n
R2 Score: {r2:.3f}''')

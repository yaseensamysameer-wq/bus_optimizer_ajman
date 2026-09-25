import pandas as pd
import numpy as np

# =========================================================
# BUS PASSENGER DEMAND DATA SIMULATOR
# Date range: 2024-08-07 to 2026-08-07
# Time: 05:00 to 00:00, every 30 minutes
# =========================================================

# ---------------------------------------------------------
# 1. RANDOM SEED
# ---------------------------------------------------------

np.random.seed(42)


# ---------------------------------------------------------
# 2. BASIC SETTINGS
# ---------------------------------------------------------

START_DATE = "2024-08-07"
END_DATE = "2026-08-07"

AREAS = [
    "al nuaimia",
    "al rashidiya",
    "al rawda",
    "al bustan",
    "al zorah",
    "ajman industrial area",
    "al jurf"
]

ROUTES = [
    "route AJ1",
    "route AJ2",
    "route AJ3",
    "route E400",
    "route E411"
]


# ---------------------------------------------------------
# 3. CREATE DATES
# ---------------------------------------------------------

dates = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="D"
)


# ---------------------------------------------------------
# 4. CREATE TIMES
# ---------------------------------------------------------
# 05:00, 05:30, 06:00, ...
# 23:30, 00:00
#
# We use one fake date while generating the time range
# because 00:00 occurs after 23:30.

time_range = pd.date_range(
    start="2024-08-07 05:00",
    end="2024-08-08 00:00",
    freq="30min"
)

times = time_range.time


# ---------------------------------------------------------
# 5. BASE DEMAND BY AREA
# ---------------------------------------------------------
# Larger number = naturally higher passenger demand.

AREA_BASE_DEMAND = {
    "al nuaimia": 75,
    "al rashidiya": 82,
    "al rawda": 60,
    "al bustan": 68,
    "al zorah": 45,
    "ajman industrial area": 88,
    "al jurf": 78
}


# ---------------------------------------------------------
# 6. ROUTE CAPACITY
# ---------------------------------------------------------

ROUTE_CAPACITY = {
    "route AJ1": 45,
    "route AJ2": 50,
    "route AJ3": 55,
    "route E400": 60,
    "route E411": 65
}


# ---------------------------------------------------------
# 7. AREA -> ROUTE PROBABILITIES
# ---------------------------------------------------------
# The probabilities for each area add up to 1.0.
# This makes certain routes more common in certain areas.

AREA_ROUTE_WEIGHTS = {

    "al nuaimia": {
        "route AJ1": 0.30,
        "route AJ2": 0.30,
        "route AJ3": 0.15,
        "route E400": 0.15,
        "route E411": 0.10
    },

    "al rashidiya": {
        "route AJ1": 0.20,
        "route AJ2": 0.25,
        "route AJ3": 0.15,
        "route E400": 0.30,
        "route E411": 0.10
    },

    "al rawda": {
        "route AJ1": 0.25,
        "route AJ2": 0.20,
        "route AJ3": 0.25,
        "route E400": 0.20,
        "route E411": 0.10
    },

    "al bustan": {
        "route AJ1": 0.20,
        "route AJ2": 0.20,
        "route AJ3": 0.20,
        "route E400": 0.25,
        "route E411": 0.15
    },

    "al zorah": {
        "route AJ1": 0.30,
        "route AJ2": 0.15,
        "route AJ3": 0.20,
        "route E400": 0.10,
        "route E411": 0.25
    },

    "ajman industrial area": {
        "route AJ1": 0.30,
        "route AJ2": 0.20,
        "route AJ3": 0.30,
        "route E400": 0.05,
        "route E411": 0.15
    },

    "al jurf": {
        "route AJ1": 0.20,
        "route AJ2": 0.25,
        "route AJ3": 0.30,
        "route E400": 0.10,
        "route E411": 0.15
    }
}


# ---------------------------------------------------------
# 8. DAY-OF-WEEK EFFECT
# ---------------------------------------------------------

DAY_EFFECT = {
    "Monday": 1.05,
    "Tuesday": 1.10,
    "Wednesday": 1.08,
    "Thursday": 1.12,
    "Friday": 0.78,
    "Saturday": 0.92,
    "Sunday": 0.88
}


# ---------------------------------------------------------
# 9. ROUTE DEMAND EFFECT
# ---------------------------------------------------------
# Some routes naturally carry more passengers.

ROUTE_DEMAND_MULTIPLIER = {
    "route AJ1": 1.00,
    "route AJ2": 1.05,
    "route AJ3": 1.08,
    "route E400": 1.15,
    "route E411": 1.20
}


# ---------------------------------------------------------
# 10. AREA TRAFFIC EFFECT
# ---------------------------------------------------------

AREA_TRAFFIC = {
    "al nuaimia": 5,
    "al rashidiya": 6,
    "al rawda": 4,
    "al bustan": 5,
    "al zorah": 2,
    "ajman industrial area": 8,
    "al jurf": 7
}


# =========================================================
# FUNCTIONS
# =========================================================


# ---------------------------------------------------------
# 11. TIME-OF-DAY DEMAND
# ---------------------------------------------------------

def get_time_multiplier(hour, minute):

    decimal_hour = hour + minute / 60

    # 05:00 - 06:00
    if 5 <= decimal_hour < 6:
        return 0.35

    # 06:00 - 07:00
    elif 6 <= decimal_hour < 7:
        return 0.65

    # Morning rush
    elif 7 <= decimal_hour < 9:
        return 1.45

    # 09:00 - 11:00
    elif 9 <= decimal_hour < 11:
        return 1.00

    # 11:00 - 13:00
    elif 11 <= decimal_hour < 13:
        return 0.90

    # 13:00 - 15:00
    elif 13 <= decimal_hour < 15:
        return 1.05

    # 15:00 - 17:00
    elif 15 <= decimal_hour < 17:
        return 1.10

    # Evening rush
    elif 17 <= decimal_hour < 20:
        return 1.50

    # 20:00 - 22:00
    elif 20 <= decimal_hour < 22:
        return 1.05

    # 22:00 - 23:30
    elif 22 <= decimal_hour < 23.5:
        return 0.65

    # Midnight
    else:
        return 0.40


# ---------------------------------------------------------
# 12. AREA-SPECIFIC TIME EFFECT
# ---------------------------------------------------------

def get_area_time_multiplier(area, hour, minute):

    decimal_hour = hour + minute / 60

    # Industrial area:
    # Strong during working hours.
    if area == "ajman industrial area":

        if 6 <= decimal_hour < 9:
            return 1.20

        elif 9 <= decimal_hour < 16:
            return 1.35

        elif 16 <= decimal_hour < 20:
            return 1.00

        else:
            return 0.55

    # Al Zorah:
    # Lower morning demand but stronger evenings/weekends.
    elif area == "al zorah":

        if 6 <= decimal_hour < 9:
            return 0.70

        elif 17 <= decimal_hour < 21:
            return 1.25

        elif 21 <= decimal_hour <= 23.5:
            return 1.30

        else:
            return 0.85

    # Al Nuaimia
    elif area == "al nuaimia":

        if 7 <= decimal_hour < 9:
            return 1.15

        elif 17 <= decimal_hour < 20:
            return 1.20

        else:
            return 1.00

    # Al Rashidiya
    elif area == "al rashidiya":

        if 7 <= decimal_hour < 9:
            return 1.20

        elif 17 <= decimal_hour < 21:
            return 1.15

        else:
            return 1.00

    # Al Rawda
    elif area == "al rawda":

        if 7 <= decimal_hour < 9:
            return 1.10

        elif 17 <= decimal_hour < 20:
            return 1.15

        else:
            return 1.00

    # Al Bustan
    elif area == "al bustan":

        if 8 <= decimal_hour < 10:
            return 1.10

        elif 17 <= decimal_hour < 21:
            return 1.15

        else:
            return 1.00

    # Al Jurf
    elif area == "al jurf":

        if 6 <= decimal_hour < 9:
            return 1.15

        elif 17 <= decimal_hour < 20:
            return 1.20

        else:
            return 1.00

    return 1.00


# ---------------------------------------------------------
# 13. WEEKDAY + AREA EFFECT
# ---------------------------------------------------------

def get_weekday_area_multiplier(day, area):

    multiplier = 1.0

    # Industrial area is weaker on weekends.
    if area == "ajman industrial area":

        if day == "Friday":
            multiplier *= 0.60

        elif day == "Saturday":
            multiplier *= 0.72

    # Al Zorah becomes more popular on weekends.
    if area == "al zorah":

        if day == "Friday":
            multiplier *= 1.25

        elif day == "Saturday":
            multiplier *= 1.35

        elif day == "Sunday":
            multiplier *= 1.15

    # Strong weekday commuting.
    if area in ["al nuaimia", "al rashidiya"]:

        if day in ["Monday", "Tuesday", "Wednesday", "Thursday"]:
            multiplier *= 1.08

    # Al Jurf also has stronger weekday demand.
    if area == "al jurf":

        if day in ["Monday", "Tuesday", "Wednesday", "Thursday"]:
            multiplier *= 1.10

    return multiplier


# ---------------------------------------------------------
# 14. TRAFFIC DELAY
# ---------------------------------------------------------

def calculate_traffic_delay(
    day,
    area,
    hour,
    minute,
    passenger_demand
):

    decimal_hour = hour + minute / 60

    # Base traffic according to time.

    if 7 <= decimal_hour < 9:
        traffic_base = 12

    elif 16 <= decimal_hour < 20:
        traffic_base = 15

    elif 9 <= decimal_hour < 16:
        traffic_base = 6

    elif 20 <= decimal_hour < 22:
        traffic_base = 7

    else:
        traffic_base = 3

    # Start with time + area traffic.
    delay = (
        traffic_base
        + AREA_TRAFFIC[area]
    )

    # Higher passenger demand slightly increases delay.
    if passenger_demand > 100:
        delay += 3

    elif passenger_demand > 70:
        delay += 1

    # Al Zorah Friday evening traffic.
    if (
        day == "Friday"
        and area == "al zorah"
    ):
        delay += 4

    # Random variation.
    delay += np.random.normal(0, 2)

    # Delay cannot be negative.
    delay = max(0, delay)

    return round(delay, 1)


# =========================================================
# 15. GENERATE DATA
# =========================================================

rows = []

for date in dates:

    day = date.strftime("%A")

    for time_value in times:

        hour = time_value.hour
        minute = time_value.minute

        time_multiplier = get_time_multiplier(
            hour,
            minute
        )

        for area in AREAS:

            # ---------------------------------------------
            # Select a route based on the area.
            # ---------------------------------------------

            route_names = list(
                AREA_ROUTE_WEIGHTS[area].keys()
            )

            route_probabilities = list(
                AREA_ROUTE_WEIGHTS[area].values()
            )

            bus_route = np.random.choice(
                route_names,
                p=route_probabilities
            )

            # ---------------------------------------------
            # Calculate passenger demand.
            # ---------------------------------------------

            base_demand = AREA_BASE_DEMAND[area]

            area_time_multiplier = (
                get_area_time_multiplier(
                    area,
                    hour,
                    minute
                )
            )

            weekday_area_multiplier = (
                get_weekday_area_multiplier(
                    day,
                    area
                )
            )

            demand = (
                base_demand
                * DAY_EFFECT[day]
                * time_multiplier
                * area_time_multiplier
                * weekday_area_multiplier
                * ROUTE_DEMAND_MULTIPLIER[bus_route]
            )

            # Add realistic random variation.
            demand += np.random.normal(0, 7)

            # Demand must be at least 5 passengers.
            passenger_demand = max(
                5,
                int(round(demand))
            )

            # ---------------------------------------------
            # Capacity.
            # ---------------------------------------------

            base_capacity = ROUTE_CAPACITY[bus_route]

            capacity_variation = np.random.choice(
                [-5, 0, 0, 0, 5]
            )

            capacity_limit = max(
                30,
                base_capacity + capacity_variation
            )

            # ---------------------------------------------
            # Traffic delay.
            # ---------------------------------------------

            traffic_delay_mins = calculate_traffic_delay(
                day=day,
                area=area,
                hour=hour,
                minute=minute,
                passenger_demand=passenger_demand
            )

            # ---------------------------------------------
            # Store row.
            # ---------------------------------------------

            rows.append({
                "date": date,
                "day": day,
                "time": time_value.strftime("%H:%M"),
                "area": area,
                "bus_route": bus_route,
                "passenger_demand": passenger_demand,
                "capacity_limit": capacity_limit,
                "traffic_delay_mins": traffic_delay_mins
            })


# =========================================================
# 16. CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(rows)
df.to_csv('data/passengers.csv')


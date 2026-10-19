
import math
import pickle
import random
import time
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# =========================================================
# PAGE SETTINGS
# =========================================================
st.set_page_config(
    page_title="AI Smart College Bus",
    page_icon="🚌",
    layout="wide",
)

MODEL_PATH = Path(__file__).with_name("bus_eta_model.pkl")
TICK_SECONDS = 2.0


# =========================================================
# DEMO ROUTES
# =========================================================
ROUTES = {
    "Bus 12 - Yellow Route": [
        {"stop": "College Depot", "km": 0.0},
        {"stop": "City Library", "km": 2.0},
        {"stop": "Student Cafe", "km": 4.0},
        {"stop": "Main Gate Stop", "km": 7.0},
        {"stop": "Engineering Block", "km": 8.5},
    ],
    "Bus 7 - Blue Route": [
        {"stop": "North Depot", "km": 0.0},
        {"stop": "Park Junction", "km": 1.8},
        {"stop": "Central Hospital", "km": 3.6},
        {"stop": "Hostel Junction", "km": 5.2},
        {"stop": "College Main Gate", "km": 6.8},
    ],
}

TRAFFIC_LEVELS = ["Low", "Medium", "High"]

TRAFFIC_SPEED_RANGES = {
    "Low": (40.0, 50.0),
    "Medium": (25.0, 39.0),
    "High": (10.0, 24.0),
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def get_speed_for_traffic(traffic):
    minimum, maximum = TRAFFIC_SPEED_RANGES[traffic]
    return random.uniform(minimum, maximum)


def get_next_traffic(current_traffic):
    if random.random() < 0.25:
        return random.choice(
            [level for level in TRAFFIC_LEVELS
             if level != current_traffic]
        )
    return current_traffic


def calculate_eta(
    distance_km,
    speed_kmh,
    hour_value,
    traffic_value,
    stops_value,
):
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "bus_eta_model.pkl was not found. "
            "Keep it in the same folder as demo_app.py."
        )

    with open(MODEL_PATH, "rb") as model_file:
        model = pickle.load(model_file)

    model_input = pd.DataFrame([{
        "distance_km": float(distance_km),
        "speed_kmh": float(speed_kmh),
        "hour": int(hour_value),
        "traffic": traffic_value,
        "stops_remaining": int(stops_value),
    }])

    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is not None:
        model_input = model_input[list(feature_names)]

    prediction = float(model.predict(model_input)[0])
    return max(0.0, prediction)


def get_arrival_status(
    bus_position,
    target_km,
    simulation_running,
    passed_stop=False,
):
    """Return a status based on the simulated bus position."""

    if passed_stop:
        return (
            "⚠️ Bus has passed this stop",
            "The simulated bus position is beyond your selected stop.",
        )

    remaining = max(0.0, target_km - bus_position)

    if remaining <= 0.01:
        return (
            "✅ Bus arrived",
            "The bus has reached your selected stop in the demo.",
        )

    if remaining <= 0.5:
        return (
            "🟡 Arriving soon",
            f"The bus is approximately {remaining:.2f} km away.",
        )

    if simulation_running or bus_position > 0.01:
        return (
            "🚌 On the way",
            f"The bus is approximately {remaining:.2f} km away.",
        )

    return (
        "⏳ Waiting to start",
        "Start the simulation to see the bus move toward your stop.",
    )


# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "logged_in": False,
    "student_name": "",
    "student_id": "",
    "show_eta": False,
    "eta_value": None,
    "simulation_running": False,
    "last_tick": None,
    "sim_bus": None,
    "sim_stop": None,
    "sim_position": 0.0,
    "sim_speed": 32.0,
    "sim_traffic": "Medium",
    "sim_tick_count": 0,
    "sim_mode": "Automatic demo",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CSS DESIGN
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #fffdf5;
        color: #263238;
    }

    .stApp h1, .stApp h2, .stApp h3,
    .stApp h4, .stApp p, .stApp label {
        color: #263238;
    }

    [data-testid="stWidgetLabel"] p {
        color: #263238 !important;
        font-weight: 600 !important;
    }

    .bus-banner {
        background: linear-gradient(110deg, #ffdf4d, #ffc400);
        border: 2px solid #e6a900;
        border-radius: 30px 45px 20px 20px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: 0 5px 14px rgba(80, 60, 0, 0.12);
    }

    .bus-banner h1 {
        color: #172b4d !important;
        margin: 0;
    }

    .bus-banner p {
        color: #493900 !important;
    }

    .stButton button,
    .stFormSubmitButton button {
        background: #ffca05 !important;
        color: #172b4d !important;
        border: 2px solid #e0a800 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        min-height: 44px !important;
        opacity: 1 !important;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.12) !important;
    }

    .stButton button *,
    .stFormSubmitButton button * {
        color: #172b4d !important;
        fill: #172b4d !important;
        opacity: 1 !important;
    }

    .stButton button:hover,
    .stFormSubmitButton button:hover {
        background: #172b4d !important;
        border-color: #172b4d !important;
    }

    .stButton button:hover *,
    .stFormSubmitButton button:hover * {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    .stTextInput input {
        background-color: #ffffff;
        color: #263238;
    }

    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        color: #263238;
    }

    .stProgress > div > div > div > div {
        background-color: #ffc400;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="bus-banner">
        <h1>🚌 AI SMART COLLEGE BUS</h1>
        <p>
            🧠 AI ETA Prediction |
            🚦 Simulated Traffic |
            📍 Bus Arrival Status
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DEMO LOGIN
# =========================================================
if not st.session_state.logged_in:
    st.subheader("🎓 Student Demo Login")
    st.write("Enter any demo name and ID to open the prototype.")

    with st.form("login_form"):
        name = st.text_input(
            "Student name",
            placeholder="e.g. Rahul",
        )
        student_id = st.text_input(
            "Student ID",
            placeholder="e.g. DEMO101",
        )
        login_clicked = st.form_submit_button(
            "🔐 Login to Demo",
            use_container_width=True,
        )

    if login_clicked:
        if name.strip() and student_id.strip():
            st.session_state.student_name = name.strip()
            st.session_state.student_id = student_id.strip()
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.warning("Please enter both fields.")

    st.info("Demo login only; this is not secure authentication.")
    st.stop()


# =========================================================
# WELCOME / LOGOUT
# =========================================================
welcome_col, logout_col = st.columns([4, 1])

with welcome_col:
    st.markdown(f"### 👋 Welcome, {st.session_state.student_name}")

with logout_col:
    if st.button("🚪 Log out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.show_eta = False
        st.session_state.simulation_running = False
        st.rerun()

st.divider()


# =========================================================
# ROUTE AND STOP SELECTION
# =========================================================
left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("📍 Your Bus Journey")

    selected_bus = st.selectbox(
        "Select your bus",
        list(ROUTES.keys()),
        key="selected_bus",
    )

    route = ROUTES[selected_bus]
    stop_names = [item["stop"] for item in route]

    selected_stop = st.selectbox(
        "📍 Select your boarding stop",
        stop_names,
        index=min(2, len(stop_names) - 1),
        key=f"selected_stop_{selected_bus}",
    )

    target = next(
        item for item in route
        if item["stop"] == selected_stop
    )

    target_km = float(target["km"])
    route_length = float(route[-1]["km"])

    # Reset when the selected bus or stop changes.
    if (
        st.session_state.sim_bus != selected_bus
        or st.session_state.sim_stop != selected_stop
    ):
        st.session_state.sim_bus = selected_bus
        st.session_state.sim_stop = selected_stop
        st.session_state.sim_position = 0.0
        st.session_state.sim_traffic = "Medium"
        st.session_state.sim_speed = get_speed_for_traffic("Medium")
        st.session_state.sim_tick_count = 0
        st.session_state.last_tick = None
        st.session_state.simulation_running = False
        st.session_state.show_eta = False
        st.session_state.eta_value = None

    st.markdown("#### 🚦 Bus Simulation")

    st.info(
        "Demo only: bus speed, traffic, and position are simulated. "
        "No live GPS or real-time traffic feed is connected."
    )

    sim_mode = st.radio(
        "Simulation mode",
        ["Automatic demo", "Manual demo"],
        horizontal=True,
        key="mode_radio",
    )

    if sim_mode != st.session_state.sim_mode:
        st.session_state.sim_mode = sim_mode
        st.session_state.simulation_running = False
        st.session_state.last_tick = None
        st.rerun()

    # -----------------------------------------------------
    # AUTOMATIC SIMULATION
    # -----------------------------------------------------
    if sim_mode == "Automatic demo":
        start_col, pause_col, reset_col = st.columns(3)

        with start_col:
            if st.button("▶ Start", use_container_width=True):
                if st.session_state.sim_position >= target_km:
                    st.session_state.sim_position = 0.0

                st.session_state.simulation_running = True
                st.session_state.last_tick = time.time()
                st.session_state.sim_speed = get_speed_for_traffic(
                    st.session_state.sim_traffic
                )
                st.rerun()

        with pause_col:
            if st.button("⏸ Pause", use_container_width=True):
                st.session_state.simulation_running = False
                st.session_state.last_tick = None
                st.rerun()

        with reset_col:
            if st.button("↺ Reset", use_container_width=True):
                st.session_state.sim_position = 0.0
                st.session_state.sim_traffic = "Medium"
                st.session_state.sim_speed = get_speed_for_traffic("Medium")
                st.session_state.sim_tick_count = 0
                st.session_state.simulation_running = False
                st.session_state.last_tick = None
                st.session_state.show_eta = False
                st.session_state.eta_value = None
                st.rerun()

        if st.session_state.simulation_running:
            now = time.time()
            last_tick = st.session_state.last_tick or now
            elapsed = max(0.0, min(now - last_tick, 5.0))
            st.session_state.last_tick = now

            if st.session_state.sim_tick_count % 5 == 0:
                st.session_state.sim_traffic = get_next_traffic(
                    st.session_state.sim_traffic
                )

            traffic = st.session_state.sim_traffic
            target_speed = get_speed_for_traffic(traffic)

            current_speed = float(st.session_state.sim_speed)
            max_change = 3.0
            difference = target_speed - current_speed

            if abs(difference) <= max_change:
                new_speed = target_speed
            else:
                new_speed = current_speed + (
                    max_change if difference > 0 else -max_change
                )

            min_speed, max_speed = TRAFFIC_SPEED_RANGES[traffic]
            new_speed = max(min_speed, min(max_speed, new_speed))
            st.session_state.sim_speed = new_speed

            distance_moved = new_speed * elapsed / 3600.0

            st.session_state.sim_position = min(
                target_km,
                st.session_state.sim_position + distance_moved,
            )

            st.session_state.sim_tick_count += 1

            if st.session_state.sim_position >= target_km:
                st.session_state.simulation_running = False
                st.session_state.last_tick = None

            if st.session_state.simulation_running:
                st_autorefresh(
                    interval=int(TICK_SECONDS * 1000),
                    key=f"auto_refresh_{selected_bus}_{selected_stop}",
                )

        bus_position = float(st.session_state.sim_position)
        speed = float(st.session_state.sim_speed)
        traffic = st.session_state.sim_traffic

    # -----------------------------------------------------
    # MANUAL SIMULATION
    # -----------------------------------------------------
    else:
        st.session_state.simulation_running = False
        st.session_state.last_tick = None

        bus_position = st.slider(
            "Bus position from route start (km)",
            min_value=0.0,
            max_value=route_length,
            value=min(
                float(st.session_state.sim_position),
                route_length,
            ),
            step=0.1,
            key=f"manual_position_{selected_bus}_{selected_stop}",
        )

        traffic = st.selectbox(
            "Traffic level",
            TRAFFIC_LEVELS,
            index=TRAFFIC_LEVELS.index(
                st.session_state.sim_traffic
            ),
            key=f"manual_traffic_{selected_bus}_{selected_stop}",
        )

        min_speed, max_speed = TRAFFIC_SPEED_RANGES[traffic]

        speed = st.slider(
            "Assumed speed for selected traffic (km/h)",
            min_value=int(min_speed),
            max_value=int(max_speed),
            value=max(
                int(min_speed),
                min(int(st.session_state.sim_speed), int(max_speed)),
            ),
            key=f"manual_speed_{selected_bus}_{selected_stop}_{traffic}",
        )

        st.session_state.sim_position = float(bus_position)
        st.session_state.sim_speed = float(speed)
        st.session_state.sim_traffic = traffic

    # -----------------------------------------------------
    # CURRENT SPEED AND TRAFFIC
    # -----------------------------------------------------
    st.metric("🚍 Current simulated speed", f"{speed:.1f} km/h")
    st.metric("🚦 Simulated traffic", traffic)

    min_speed, max_speed = TRAFFIC_SPEED_RANGES[traffic]
    st.caption(
        f"Configured speed range for {traffic.lower()} traffic: "
        f"{min_speed:.0f}–{max_speed:.0f} km/h."
    )

    if sim_mode == "Automatic demo":
        if st.session_state.simulation_running:
            st.success(
                "Simulation running — speed and traffic update automatically."
            )
        elif bus_position >= target_km:
            st.success("Bus reached the selected stop in the demo.")
        else:
            st.caption("Press Start to begin the automatic simulation.")


# =========================================================
# DISTANCE AND REMAINING STOPS
# =========================================================
remaining_distance = max(0.0, target_km - bus_position)

passed_indices = [
    index for index, item in enumerate(route)
    if item["km"] <= bus_position
]

current_index = max(passed_indices) if passed_indices else 0
target_index = stop_names.index(selected_stop)

stops_remaining = max(0, target_index - current_index)
hour = time.localtime().tm_hour

passed_stop = bus_position > target_km + 0.01

arrival_title, arrival_description = get_arrival_status(
    bus_position=bus_position,
    target_km=target_km,
    simulation_running=st.session_state.simulation_running,
    passed_stop=passed_stop,
)


# =========================================================
# ETA AND ARRIVAL STATUS PANEL
# =========================================================
with right:
    st.subheader("⏱️ Your Bus Arrival Estimate")

    st.write(f"**Selected bus:** {selected_bus}")
    st.write(f"**Your boarding stop:** {selected_stop}")
    st.write(f"**Simulated bus position:** {bus_position:.2f} km")

    st.divider()
    st.markdown("### 📢 Bus Arrival Status")

    if "Bus arrived" in arrival_title:
        st.success(f"### {arrival_title}\n\n{arrival_description}")
    elif "Arriving soon" in arrival_title:
        st.warning(f"### {arrival_title}\n\n{arrival_description}")
    elif "passed this stop" in arrival_title:
        st.error(f"### {arrival_title}\n\n{arrival_description}")
    elif "On the way" in arrival_title:
        st.info(f"### {arrival_title}\n\n{arrival_description}")
    else:
        st.info(f"### {arrival_title}\n\n{arrival_description}")

    st.metric("Distance remaining", f"{remaining_distance:.2f} km")
    st.metric("Stops remaining", stops_remaining)

    if st.button(
        "🔮 Predict Arrival Time",
        type="primary",
        use_container_width=True,
        key="predict_eta_button",
    ):
        st.session_state.show_eta = True

    if remaining_distance <= 0.01:
        st.success("🚌 The bus is at your selected stop!")

        if st.session_state.show_eta:
            st.metric("Predicted ETA", "0 minutes")
            st.session_state.eta_value = 0.0

    elif st.session_state.show_eta:
        try:
            eta = calculate_eta(
                remaining_distance,
                speed,
                hour,
                traffic.lower(),
                stops_remaining,
            )

            st.session_state.eta_value = eta

            st.metric("Predicted ETA", f"{eta:.1f} minutes")

            st.caption(
                "The estimate uses the saved ML model. "
                "Results depend on the model and training data."
            )

        except Exception as error:
            st.error(
                "ETA prediction failed. Check the model's expected "
                "feature names and traffic encoding."
            )
            st.code(str(error))

    else:
        st.caption(
            "Click Predict Arrival Time to display the estimated arrival."
        )

    st.markdown("#### 🛣️ Demo Route Stops")

    for item in route:
        if item["stop"] == selected_stop:
            st.markdown(
                f"🎯 **{item['stop']} — {item['km']:.1f} km**"
            )
        elif item["km"] <= bus_position:
            st.markdown(
                f"✅ {item['stop']} — {item['km']:.1f} km"
            )
        else:
            st.markdown(
                f"⚪ {item['stop']} — {item['km']:.1f} km"
            )


# =========================================================
# ROUTE PROGRESS
# =========================================================
st.divider()
st.subheader("📍 Sample Route Progress")
st.caption("Illustrative route progress, not live GPS.")

progress = max(
    0.0,
    min(100.0, (bus_position / route_length) * 100.0),
)

st.markdown(f"**🚌 Bus journey — {progress:.0f}% completed**")
st.progress(progress / 100.0)

milestones = [
    ("Start", 0),
    ("25%", 25),
    ("50%", 50),
    ("75%", 75),
    ("Destination", 100),
]

milestone_columns = st.columns(5)

for column, (label, percentage) in zip(milestone_columns, milestones):
    with column:
        if progress >= percentage:
            st.markdown(f"🟡 **{label}**")
        else:
            st.markdown(f"⚪ {label}")


# =========================================================
# SPEED RANGE SUMMARY
# =========================================================
st.divider()
st.subheader("🚦 Traffic and Speed Rules")

speed_col1, speed_col2, speed_col3 = st.columns(3)

with speed_col1:
    st.markdown("### 🟢 Low Traffic")
    st.metric("Speed range", "40–50 km/h")

with speed_col2:
    st.markdown("### 🟡 Medium Traffic")
    st.metric("Speed range", "25–39 km/h")

with speed_col3:
    st.markdown("### 🔴 High Traffic")
    st.metric("Speed range", "10–24 km/h")


# =========================================================
# DISCLAIMER
# =========================================================
st.divider()

st.warning(
    "Prototype limitations: bus routes and distances are fictional. "
    "Speed, traffic, and bus position are simulated, not measured. "
    "No live GPS, real-time traffic feed, or secure authentication "
    "is connected. ETA quality depends on the model and its training data."
)

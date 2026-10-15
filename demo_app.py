
import pickle
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="AI Smart College Bus",
    page_icon="🚌",
    layout="wide"
)

# ---------------- DEMO ROUTES ----------------
ROUTES = {
    "Bus 12 - Yellow Route": [
        {"stop": "College Depot", "km": 0.0},
        {"stop": "City Library", "km": 2.0},
        {"stop": "Market Stop", "km": 4.0},
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

MODEL_PATH = Path(__file__).with_name("bus_eta_model.pkl")

# ---------------- CSS DESIGN ----------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #fffdf5;
        color: #263238;
    }

    .stApp p,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp li {
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

    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        color: #263238;
    }

    div[data-baseweb="select"] * {
        color: #263238;
    }

    .route-card {
        background: #ffffff;
        padding: 22px 18px;
        border-radius: 16px;
        border: 1px solid #f0e5c6;
        margin-top: 10px;
    }

    .route-track {
        height: 8px;
        background: #e5e7eb;
        border-radius: 20px;
        margin: 26px 10px 20px 10px;
        overflow: hidden;
    }

    .route-fill {
        height: 8px;
        background: #ffc400;
        border-radius: 20px;
    }

    .route-stops {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 3px;
    }

    .route-stop {
        width: 20%;
        text-align: center;
        color: #172b4d !important;
        font-size: 12px;
        font-weight: 600;
    }

    .route-dot {
        display: inline-block;
        height: 16px;
        width: 16px;
        border: 4px solid #d5d9df;
        background: white;
        border-radius: 50%;
        margin-bottom: 8px;
    }

    .route-stop.done .route-dot {
        border-color: #e6a900;
        background: #ffc400;
    }

    .route-stop.current .route-dot {
        border-color: #172b4d;
        background: #ffc400;
        box-shadow: 0 0 0 4px #ffed9e;
    }

    .route-bus {
        font-size: 25px;
        margin-bottom: 5px;
    }

    .stButton button {
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- HEADER ----------------
st.markdown(
    """
    <div class="bus-banner">
        <h1>🚌 AI SMART COLLEGE BUS</h1>
        <p>🧠 Smart travel-time estimation |
        🚦 Traffic-aware inputs | ⏱️ ETA prediction</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- DEMO LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("🎓 Student Demo Login")
    st.write("Enter any demo name and ID to open the prototype.")

    with st.form("login_form"):
        name = st.text_input("Student name", placeholder="e.g. Rahul")
        student_id = st.text_input("Student ID", placeholder="e.g. DEMO101")
        login = st.form_submit_button("Login to Demo")

    if login:
        if name.strip() and student_id.strip():
            st.session_state.student_name = name.strip()
            st.session_state.student_id = student_id.strip()
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.warning("Please enter both fields.")

    st.info("Demo login only. It is not secure student authentication.")
    st.stop()

# ---------------- WELCOME ----------------
welcome_col, logout_col = st.columns([4, 1])

with welcome_col:
    st.markdown(
        f"### 👋 Welcome, {st.session_state.student_name} "
        f"({st.session_state.student_id})"
    )

with logout_col:
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# ---------------- MAIN LAYOUT ----------------
left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("📍 Your Bus Journey")

    selected_bus = st.selectbox(
        "Select your bus",
        list(ROUTES.keys())
    )

    route = ROUTES[selected_bus]
    stop_names = [stop["stop"] for stop in route]

    selected_stop = st.selectbox(
        "Select your target stop",
        stop_names[1:],
        index=min(2, len(stop_names) - 2)
    )

    st.markdown("#### 🧪 Simulated Bus Status")
    st.caption(
        "Move the slider to simulate the bus position. "
        "This is not live GPS tracking."
    )

    route_length = float(route[-1]["km"])

    bus_position = st.slider(
        "Bus position from route start (km)",
        min_value=0.0,
        max_value=route_length,
        value=min(2.5, route_length),
        step=0.1
    )

    speed = st.slider(
        "Assumed average speed (km/h)",
        min_value=10,
        max_value=50,
        value=30
    )

    hour = st.slider(
        "Time of day (hour)",
        min_value=6,
        max_value=22,
        value=8
    )

    traffic = st.selectbox(
        "Assumed traffic",
        ["low", "medium", "high"],
        index=1
    )

# ---------------- CALCULATE DISTANCE ----------------
target = next(
    stop for stop in route
    if stop["stop"] == selected_stop
)

remaining_distance = round(
    target["km"] - bus_position, 2
)

passed_stops = [
    i for i, stop in enumerate(route)
    if stop["km"] <= bus_position
]

current_index = max(passed_stops) if passed_stops else 0
target_index = stop_names.index(selected_stop)

stops_remaining = max(0, target_index - current_index)

# ---------------- ETA PANEL ----------------
with right:
    st.subheader("⏱️ Estimated Arrival")

    st.write(f"**Selected bus:** {selected_bus}")
    st.write(f"**Target stop:** {selected_stop}")
    st.write(f"**Simulated position:** {bus_position:.1f} km")

    if remaining_distance < 0:
        st.error(
            "The bus has already passed this stop. "
            "Move the bus-position slider earlier or choose a later stop."
        )
    else:
        st.metric(
            "Distance remaining",
            f"{remaining_distance:.2f} km"
        )

        st.metric("Stops remaining", stops_remaining)

        predict = st.button(
            "🔮 Predict Arrival Time",
            type="primary",
            use_container_width=True
        )

        if predict:
            if remaining_distance == 0:
                st.success("The bus is at your selected stop!")
                st.metric("Predicted ETA", "0 minutes")

            elif not MODEL_PATH.exists():
                st.error(
                    "bus_eta_model.pkl was not found. "
                    "Keep it in the same folder as demo_app.py."
                )

            else:
                try:
                    with open(MODEL_PATH, "rb") as model_file:
                        model = pickle.load(model_file)

                    input_data = pd.DataFrame([{
                        "distance_km": remaining_distance,
                        "speed_kmh": speed,
                        "hour": hour,
                        "traffic": traffic,
                        "stops_remaining": stops_remaining,
                    }])

                    eta = max(
                        0.0,
                        float(model.predict(input_data)[0])
                    )

                    st.metric("Predicted ETA", f"{eta:.1f} minutes")
                    st.caption(
                        "Demo estimate from the saved ML model. "
                        "Actual arrival time may differ."
                    )

                except Exception as error:
                    st.error(
                        "The model could not process these inputs. "
                        "Check that the feature columns match the training data."
                    )
                    st.code(str(error))

    # ---------------- ROUTE STOPS ----------------
    st.markdown("#### 🛣️ Demo Route Stops")

    for stop in route:
        if stop["stop"] == selected_stop:
            st.markdown(
                f"🎯 **{stop['stop']} — {stop['km']:.1f} km**"
            )
        elif stop["km"] <= bus_position:
            st.markdown(
                f"✅ {stop['stop']} — {stop['km']:.1f} km"
            )
        else:
            st.markdown(
                f"⚪ {stop['stop']} — {stop['km']:.1f} km"
            )

# ---------------- ROUTE PROGRESS BAR ----------------

# ---------------- ROUTE PROGRESS BAR ----------------
st.divider()
st.subheader("📍 Sample Route Progress")
st.caption(
    "Illustrative progress based on the slider — not live GPS tracking."
)

progress = max(
    0.0,
    min(100.0, (bus_position / route_length) * 100.0)
)

milestones = [
    ("Start", 0),
    ("25%", 25),
    ("50%", 50),
    ("75%", 75),
    ("Destination", 100),
]

# Draw the progress line using Streamlit columns and widgets
st.markdown(
    f"**🚌 Bus journey** — {progress:.0f}% completed"
)

st.progress(progress / 100.0)

columns = st.columns(5)

for column, (label, percent) in zip(columns, milestones):
    with column:
        if progress >= percent:
            st.markdown(f"🟡 **{label}**")
        else:
            st.markdown(f"⚪ {label}")


# ---------------- DISCLAIMER ----------------
st.divider()
st.warning(
    "Prototype limitations: routes and distances are fictional. "
    "Bus position, speed, time and traffic are manually simulated. "
    "This app has no live GPS, live traffic or secure authentication."
)

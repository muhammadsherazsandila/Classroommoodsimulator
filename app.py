import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from collections import Counter

# ============================================================
# CLASSROOM MOOD SIMULATOR
# ============================================================

st.set_page_config(
    page_title="Classroom Mood Simulator",
    page_icon="🎓",
    layout="wide"
)

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------

if "temperature" not in st.session_state:
    st.session_state.temperature = 25

if "students" not in st.session_state:
    st.session_state.students = []

if "history" not in st.session_state:
    st.session_state.history = []

if "simulation_number" not in st.session_state:
    st.session_state.simulation_number = 0


# ------------------------------------------------------------
# TEMPERATURE-MOOD MODEL
# ------------------------------------------------------------

def mood_probabilities(temp):

    """
    Returns probabilities for:

    Excited
    Happy
    Neutral
    Uncomfortable
    """

    # Very cold
    if temp <= 10:
        excited = 0.02
        happy = 0.08
        neutral = 0.25
        bad = 0.65

    # 10-20 C
    elif temp <= 20:
        x = (temp - 10) / 10

        excited = 0.02 + x * 0.15
        happy = 0.08 + x * 0.30
        neutral = 0.25 + x * 0.10
        bad = 0.65 - x * 0.55

    # 20-25 C
    elif temp <= 25:
        x = (temp - 20) / 5

        excited = 0.17 + x * 0.08
        happy = 0.38 + x * 0.12
        neutral = 0.35 - x * 0.10
        bad = 0.10 - x * 0.10

    # 25-30 C
    elif temp <= 30:
        x = (temp - 25) / 5

        excited = 0.25 - x * 0.10
        happy = 0.50 - x * 0.10
        neutral = 0.25 + x * 0.10
        bad = 0.00 + x * 0.10

    # 30-40 C
    elif temp <= 40:
        x = (temp - 30) / 10

        excited = 0.15 - x * 0.10
        happy = 0.40 - x * 0.20
        neutral = 0.35 - x * 0.05
        bad = 0.10 + x * 0.35

    # 40-50 C
    else:
        x = (temp - 40) / 10

        excited = 0.05 - x * 0.05
        happy = 0.20 - x * 0.15
        neutral = 0.30 - x * 0.20
        bad = 0.45 + x * 0.40

    probabilities = {
        "Excited": excited,
        "Happy": happy,
        "Neutral": neutral,
        "Uncomfortable": bad
    }

    # Make absolutely sure probabilities add to 1
    total = sum(probabilities.values())

    for mood in probabilities:
        probabilities[mood] /= total

    return probabilities


# ------------------------------------------------------------
# GENERATE CLASS
# ------------------------------------------------------------

def generate_students(temp, number_students=30):

    probabilities = mood_probabilities(temp)

    moods = list(probabilities.keys())
    probs = list(probabilities.values())

    students = np.random.choice(
        moods,
        size=number_students,
        p=probs
    )

    return list(students)


# ------------------------------------------------------------
# MOOD INFORMATION
# ------------------------------------------------------------

mood_emoji = {
    "Excited": "😄",
    "Happy": "😊",
    "Neutral": "😐",
    "Uncomfortable": "😞"
}

mood_score = {
    "Excited": 4,
    "Happy": 3,
    "Neutral": 2,
    "Uncomfortable": 1
}


# ------------------------------------------------------------
# INITIAL SIMULATION
# ------------------------------------------------------------

if len(st.session_state.students) == 0:

    st.session_state.students = generate_students(
        st.session_state.temperature
    )

    st.session_state.simulation_number += 1


# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

st.title("🎓 Classroom Mood Simulator")

st.markdown(
    """
    **Interactive temperature-dependent classroom model**

    Change the classroom temperature and observe how the predicted
    mood distribution of 30 students changes.
    """
)


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

st.sidebar.header("⚙️ Simulation Controls")

temperature = st.sidebar.slider(
    "🌡️ Classroom Temperature (°C)",
    min_value=10,
    max_value=50,
    value=st.session_state.temperature,
    step=1
)

st.session_state.temperature = temperature


number_students = st.sidebar.number_input(
    "👨‍🎓 Number of Students",
    min_value=5,
    max_value=100,
    value=30,
    step=1
)


if st.sidebar.button("🎲 Random Temperature", use_container_width=True):

    new_temperature = np.random.randint(10, 51)

    st.session_state.temperature = int(new_temperature)

    st.session_state.students = generate_students(
        new_temperature,
        number_students
    )

    st.session_state.simulation_number += 1

    st.rerun()


if st.sidebar.button("🔄 Run Simulation", use_container_width=True):

    st.session_state.students = generate_students(
        temperature,
        number_students
    )

    st.session_state.simulation_number += 1

    st.rerun()


if st.sidebar.button("♻️ Reset Class", use_container_width=True):

    st.session_state.temperature = 25

    st.session_state.students = generate_students(
        25,
        number_students
    )

    st.session_state.history = []

    st.session_state.simulation_number += 1

    st.rerun()


# ------------------------------------------------------------
# GET PROBABILITIES
# ------------------------------------------------------------

probabilities = mood_probabilities(temperature)


# ------------------------------------------------------------
# COUNT ACTUAL STUDENTS
# ------------------------------------------------------------

counts = Counter(st.session_state.students)

excited_count = counts["Excited"]
happy_count = counts["Happy"]
neutral_count = counts["Neutral"]
bad_count = counts["Uncomfortable"]


# ------------------------------------------------------------
# AVERAGE MOOD
# ------------------------------------------------------------

total_score = sum(
    mood_score[mood]
    for mood in st.session_state.students
)

average_mood = total_score / len(st.session_state.students)


# ------------------------------------------------------------
# TEMPERATURE STATUS
# ------------------------------------------------------------

if temperature < 18:

    status = "🥶 Classroom is relatively cold"

elif temperature <= 25:

    status = "🌤️ Comfortable classroom temperature"

elif temperature <= 30:

    status = "☀️ Classroom is becoming warm"

elif temperature <= 35:

    status = "🥵 Classroom is hot"

else:

    status = "🔥 Classroom is very hot"


# ------------------------------------------------------------
# TOP INFORMATION
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "🌡️ Temperature",
        f"{temperature} °C"
    )

with col2:

    st.metric(
        "👨‍🎓 Students",
        len(st.session_state.students)
    )

with col3:

    st.metric(
        "⭐ Average Mood",
        f"{average_mood:.2f} / 4"
    )

with col4:

    st.metric(
        "🎮 Simulation",
        st.session_state.simulation_number
    )


st.info(status)


# ------------------------------------------------------------
# CLASSROOM VISUALIZATION
# ------------------------------------------------------------

st.subheader("🏫 Live Classroom")

# Create classroom layout

columns = 6

for row in range(
    (len(st.session_state.students) + columns - 1) // columns
):

    cols = st.columns(columns)

    for col in range(columns):

        index = row * columns + col

        if index < len(st.session_state.students):

            mood = st.session_state.students[index]

            emoji = mood_emoji[mood]

            with cols[col]:

                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        border:1px solid #cccccc;
                        border-radius:12px;
                        padding:12px;
                        margin:5px;
                        background-color:#f8f8f8;
                    ">

                    <div style="font-size:42px;">
                    {emoji}
                    </div>

                    <b>Student {index + 1}</b>

                    <br>

                    <small>{mood}</small>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ------------------------------------------------------------
# PROBABILITY SECTION
# ------------------------------------------------------------

st.subheader("📊 Probability at Current Temperature")

probability_data = pd.DataFrame({

    "Mood": [
        "Excited",
        "Happy",
        "Neutral",
        "Uncomfortable"
    ],

    "Probability": [
        probabilities["Excited"] * 100,
        probabilities["Happy"] * 100,
        probabilities["Neutral"] * 100,
        probabilities["Uncomfortable"] * 100
    ],

    "Actual Students": [
        excited_count,
        happy_count,
        neutral_count,
        bad_count
    ]
})


# ------------------------------------------------------------
# EXPECTED NUMBER
# ------------------------------------------------------------

probability_data["Expected Students"] = (
    probability_data["Probability"] / 100
    * len(st.session_state.students)
)


st.dataframe(
    probability_data.style.format({
        "Probability": "{:.2f}%",
        "Expected Students": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)


# ------------------------------------------------------------
# BAR CHART
# ------------------------------------------------------------

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=probability_data["Mood"],
        y=probability_data["Probability"],
        name="Probability (%)"
    )
)

fig.update_layout(
    title="Predicted Mood Probability",
    xaxis_title="Mood",
    yaxis_title="Probability (%)",
    yaxis=dict(range=[0, 100]),
    height=400
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ------------------------------------------------------------
# ACTUAL STUDENT DISTRIBUTION
# ------------------------------------------------------------

fig2 = go.Figure()

fig2.add_trace(
    go.Bar(
        x=probability_data["Mood"],
        y=probability_data["Actual Students"],
        name="Students"
    )
)

fig2.update_layout(
    title="Actual Simulated Students by Mood",
    xaxis_title="Mood",
    yaxis_title="Number of Students",
    yaxis=dict(
        range=[0, max(10, len(st.session_state.students))]
    ),
    height=400
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ------------------------------------------------------------
# EXPECTED VS ACTUAL
# ------------------------------------------------------------

st.subheader("🔬 Model Prediction vs Simulation")

comparison = probability_data[
    [
        "Mood",
        "Expected Students",
        "Actual Students"
    ]
].copy()

st.dataframe(
    comparison.style.format({
        "Expected Students": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)


# ------------------------------------------------------------
# CLASSROOM MOOD INTERPRETATION
# ------------------------------------------------------------

if average_mood >= 3.5:

    interpretation = "🌟 Very positive classroom mood"

elif average_mood >= 2.75:

    interpretation = "😊 Generally positive classroom mood"

elif average_mood >= 2.0:

    interpretation = "😐 Mostly neutral classroom mood"

else:

    interpretation = "⚠️ Poor classroom mood"


st.success(
    f"Teacher Prediction: **{interpretation}**"
)


# ------------------------------------------------------------
# TEMPERATURE HISTORY
# ------------------------------------------------------------

st.session_state.history.append({

    "Simulation": st.session_state.simulation_number,
    "Temperature": temperature,
    "Average Mood": average_mood,
    "Excited": excited_count,
    "Happy": happy_count,
    "Neutral": neutral_count,
    "Uncomfortable": bad_count
})


# Keep last 20 simulations

st.session_state.history = (
    st.session_state.history[-20:]
)


# ------------------------------------------------------------
# HISTORY GRAPH
# ------------------------------------------------------------

if len(st.session_state.history) > 1:

    history_df = pd.DataFrame(
        st.session_state.history
    )

    st.subheader("📈 Simulation History")

    fig3 = go.Figure()

    fig3.add_trace(
        go.Scatter(
            x=history_df["Temperature"],
            y=history_df["Average Mood"],
            mode="lines+markers",
            name="Average Mood"
        )
    )

    fig3.update_layout(
        title="Temperature vs Average Classroom Mood",
        xaxis_title="Temperature (°C)",
        yaxis_title="Average Mood Score",
        yaxis=dict(range=[1, 4]),
        height=450
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


# ------------------------------------------------------------
# MODEL INFORMATION
# ------------------------------------------------------------

with st.expander("📘 About the Model"):

    st.write(
        """
        This simulation uses a stochastic temperature-dependent
        probability model.

        At every temperature, four probabilities are calculated:

        • Excited
        • Happy
        • Neutral
        • Uncomfortable

        The probabilities always add up to 100%.

        Individual students are then randomly assigned a mood
        according to these probabilities.

        Therefore, the expected number of students and the actual
        simulated number of students can be different.

        Example:

        If the probability of being Happy is 50% and there are
        30 students:

            Expected Happy Students = 30 × 0.50 = 15

        However, a particular simulation might produce 13, 15,
        16, or another number of Happy students because the
        students are generated randomly.
        """
    )


st.caption(
    "Classroom Mood Simulator | Python + Streamlit + Plotly"
)

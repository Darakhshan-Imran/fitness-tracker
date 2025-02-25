
import streamlit as st
import pandas as pd
import plotly.express as px
from database import insert_workout, insert_food, fetch_workouts, fetch_food, delete_workout, delete_food
from streamlit_option_menu import option_menu
import datetime
import sqlite3

# Set Page Title and Layout
st.set_page_config(page_title="Health & Fitness Tracker", layout="wide")

# Initialize session state for workouts
if "workouts" not in st.session_state:
    st.session_state.workouts = []

# Dark mode toggle button
theme = st.sidebar.radio("🌙 **Theme**", ["Light", "Dark"], horizontal=True)

# Apply theme colors dynamically
if theme == "Dark":
    st.markdown(
        """
       <style>
            body, .stApp { background-color: #414040; color: white; }
            .css-1d391kg, .stTextInput, .stNumberInput, .stDateInput {
                background-color: #333 !important;
                color: white !important;
            }
            /* Fix: Ensure buttons keep black text in dark mode */
            button, .stButton>button {
                color: black !important;
                background-color: white !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# Center the image
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("images/fitness_logo1.jpg", width=600)

st.title("Health & Fitness Tracker")
st.write("Welcome to your fitness tracking app!")

# Sidebar Navigation with Icons
with st.sidebar:
    menu = option_menu(
        "Select Activity", 
        ["Log Workout", "Log Food Intake", "View Progress",  "BMI Calculator"],
        icons=["activity", "cup-straw", "bar-chart", "calculator"],  
        menu_icon="list", 
        default_index=0
    )

# Function to delete a workout entry by ID
def delete_workout(workout_id):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
    conn.commit()
    conn.close()

# Function to delete a food entry by ID
def delete_food(food_id):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food WHERE id = ?", (food_id,))
    conn.commit()
    conn.close()

# ----- Log Workout -----
if menu == "Log Workout":
    st.header("Log Your Workout")
    date = st.date_input("Date")
    weight = st.number_input("Your Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)

    MET_values = {"Running": 9.8, "Cycling": 7.5, "Walking": 3.5, "Swimming": 8.0, "Strength Training": 6.0}

    with st.form("workout_form", clear_on_submit=True):
        exercise_type = st.selectbox("Select Exercise Type", list(MET_values.keys()))
        duration = st.number_input("Duration (minutes)", min_value=1)
        calories_burned = MET_values.get(exercise_type, 6.0) * weight * (duration / 60)
        
        add_workout = st.form_submit_button("➕ Add Exercise")
        if add_workout:
            st.session_state.workouts.append((exercise_type, duration, calories_burned))
            st.success(f"Added: {exercise_type} ({duration} min)")
    
    total_calories = sum(cal for _, _, cal in st.session_state.workouts)
    st.subheader(f"🔥 **Total Calories Burned: {total_calories:.2f} kcal**")

    if st.button("Save Workout"):
        for exercise_type, duration, calories in st.session_state.workouts:
            insert_workout(date, exercise_type, duration, calories)
        st.session_state.workouts.clear()
        st.success("Workout logged successfully!")

# ----- Log Food Intake -----
elif menu == "Log Food Intake":
    st.header("Log Your Meals")
    date = st.date_input("Date")
    meal = st.text_input("Meal")
    protein = st.number_input("Protein (g)", min_value=0.0)
    carbs = st.number_input("Carbs (g)", min_value=0.0)
    fats = st.number_input("Fats (g)", min_value=0.0)
    calories_intake = (protein * 4) + (carbs * 4) + (fats * 9)
    st.write(f"🍛 Estimated Calories: **{calories_intake:.2f} kcal**")
    if st.button("Save Meal"):
        insert_food(date, meal, calories_intake, protein, carbs, fats)
        st.success("Meal logged successfully!")

# ----- View Progress -----
elif menu == "View Progress":
    st.header("Your Progress")
    if st.button("🔄 Refresh Workout History"):
        workouts = fetch_workouts()
        st.success("Workout history refreshed!")

    today = datetime.date.today()
    first_day = today.replace(day=1)
    last_day = (first_day.replace(month=first_day.month % 12 + 1, day=1) - datetime.timedelta(days=1))
    date_range = pd.date_range(start=first_day, end=last_day)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏋️ Workout History")
        workouts = fetch_workouts()
        if workouts:
            df_workouts = pd.DataFrame(workouts, columns=["ID", "Date", "Exercise", "Duration", "Calories"])
            df_workouts["Date"] = pd.to_datetime(df_workouts["Date"])
            df_calendar = pd.DataFrame({"Date": date_range})
            df_workouts = df_calendar.merge(df_workouts, on="Date", how="left").fillna({"Calories": 0})
            st.dataframe(df_workouts[["Date", "Exercise", "Duration", "Calories"]])
            if df_workouts["Calories"].sum() > 0:
                fig = px.line(df_workouts, x="Date", y="Calories", markers=True, title="🔥 Calories Burned Over Time")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No workout data available yet.")
            st.markdown("### Delete Workout Entries")
            for index, row in df_workouts.iterrows():
                if pd.notna(row["ID"]):
                    if st.button(f"🗑️ Delete {row['Exercise']} on {row['Date']}", key=f"workout_{row['ID']}"):
                        delete_workout(row["ID"])
                        st.warning(f"Deleted: {row['Exercise']} on {row['Date']}")
                        st.rerun()

    with col2:
        st.subheader("🍽️ Food Intake History")
        food = fetch_food()
        if food:
            df_food = pd.DataFrame(food, columns=["ID", "Date", "Meal", "Calories", "Protein", "Carbs", "Fats"])
            df_food["Date"] = pd.to_datetime(df_food["Date"])
            df_calendar = pd.DataFrame({"Date": date_range})
            df_food = df_calendar.merge(df_food, on="Date", how="left").fillna({"Calories": 0})
            st.dataframe(df_food[["Date", "Meal", "Calories", "Protein", "Carbs", "Fats"]])
            if df_food["Calories"].sum() > 0:
                fig2 = px.bar(df_food, x="Date", y="Calories", color="Meal", title="🍛 Calories Intake Per Meal")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.write("No food intake data available yet.")
            st.markdown("### Delete Food Entries")
            for index, row in df_food.iterrows():
                if pd.notna(row["ID"]):
                    if st.button(f"🗑️ Delete {row['Meal']} on {row['Date']}", key=f"food_{row['ID']}"):
                        delete_food(row["ID"])
                        st.warning(f"Deleted: {row['Meal']} on {row['Date']}")
                        st.rerun()

# ----- BMI Calculator -----
if menu == "BMI Calculator":
    st.header("BMI Calculator")
    
    weight = st.number_input("Enter your Weight (kg)", min_value=10.0, max_value=300.0, value=70.0)
    height_cm = st.number_input("Enter your Height (cm)", min_value=50.0, max_value=250.0, value=170.0)

    if st.button("Calculate BMI"):
        height_m = height_cm / 100  # Convert height to meters
        bmi = weight / (height_m ** 2)  # BMI formula

        # Determine BMI category
        if bmi < 18.5:
            category = "Underweight"
            color = "blue"
        elif 18.5 <= bmi < 24.9:
            category = "Normal weight"
            color = "green"
        elif 25.0 <= bmi < 29.9:
            category = "Overweight"
            color = "orange"
        else:
            category = "Obese"
            color = "red"

        # Display results
        st.success(f"Your BMI is **{bmi:.2f}**")
        st.markdown(f"<h4 style='color:{color};'>Category: {category}</h4>", unsafe_allow_html=True)
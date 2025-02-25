import sqlite3

def create_tables():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS workouts (
                        id INTEGER PRIMARY KEY, 
                        date TEXT, 
                        exercise TEXT, 
                        duration INTEGER, 
                        calories INTEGER)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS food (
                        id INTEGER PRIMARY KEY, 
                        date TEXT, 
                        meal TEXT, 
                        calories INTEGER, 
                        protein REAL, 
                        carbs REAL, 
                        fats REAL)''')
    
    conn.commit()
    conn.close()

def insert_workout(date, exercise, duration, calories):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO workouts (date, exercise, duration, calories) VALUES (?, ?, ?, ?)", 
                   (date, exercise, duration, calories))
    conn.commit()
    conn.close()

def insert_food(date, meal, calories, protein, carbs, fats):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO food (date, meal, calories, protein, carbs, fats) VALUES (?, ?, ?, ?, ?, ?)", 
                   (date, meal, calories, protein, carbs, fats))
    conn.commit()
    conn.close()

def fetch_workouts():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_food():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM food")
    data = cursor.fetchall()
    conn.close()
    return data


# Function to delete a single workout entry
def delete_workout(workout_id):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workouts WHERE ID = ?", (workout_id,))
    conn.commit()
    conn.close()

# Function to delete a single food entry
def delete_food(food_id):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food WHERE ID = ?", (food_id,))
    conn.commit()
    conn.close()
# Create tables when script runs
create_tables()

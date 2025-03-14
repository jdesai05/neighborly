import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# MySQL Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "epichaibro"),
    "database": os.getenv("DB_NAME", "psdproject"),
}

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_api_key")
genai.configure(api_key=GEMINI_API_KEY)

# Function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Function to initialize database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            event_date DATE NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

init_db()

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in as admin to access this page.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session["user_id"],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user or not user[0]:
            flash("You do not have admin privileges.", "danger")
            return redirect(url_for("home"))

        return f(*args, **kwargs)
    return decorated_function

# Route to display events
@app.route("/events")
def events():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events ORDER BY event_date DESC")
    events_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("events.html", events=events_list)

# Route to add event (admin only)
@app.route("/add_event", methods=["GET", "POST"])
@admin_required
def add_event():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        event_date = request.form["event_date"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (title, description, event_date) VALUES (%s, %s, %s)", 
                       (title, description, event_date))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Event added successfully!", "success")
        return redirect(url_for("events"))

    return render_template("add_event.html")

# Route to delete event (admin only)
@app.route("/delete_event/<int:event_id>")
@admin_required
def delete_event(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Event deleted successfully!", "success")
    return redirect(url_for("events"))

# Chatbot function using Google Gemini
def simple_chatbot(user_input):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(user_input)
        return response.text if response else "I couldn't process your request."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
            conn.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Email already registered.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")

@app.route("/insert_housing", methods=["GET", "POST"])
def insert_housing():
    if request.method == "POST":
            owner_name = request.form.get("owner_name").strip()
            email = request.form.get("email").strip()
            phone = request.form.get("phone").strip()
            location = request.form.get("location").strip()
            price = request.form.get("price").strip()
            house_type = request.form.get("house_type").strip()

            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """INSERT INTO housingreg (owner_name, email, phone, location, price, house_type)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            values = (owner_name, email, phone, location, price, house_type)

            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()

            flash("House listing added successfully!", "success")
            # Change this line from 'index' to 'home'
            return redirect(url_for("home"))



@app.route("/housingreg")
def housingreg():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM housingreg")
        listings = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("insert_housing.html", listings=listings)
    except Exception as e:
        flash(f"Error fetching listings: {e}", "danger")
        return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, password, is_admin FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["is_admin"] = user["is_admin"]
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    bot_response = simple_chatbot(user_message)
    return jsonify({"response": bot_response})

#Fix for the complaintsform route to match your HTML links

@app.route("/complaintsform", methods=["POST"])
def complaintsform():
    if request.method == "POST":
        fullname = request.form.get("fullname").strip()
        email = request.form.get("email").strip()
        phone = request.form.get("phone").strip()
        complaint_type = request.form.get("complaint-type").strip()
        incident_date = request.form.get("incident-date").strip()
        complaint_details = request.form.get("complaint-details").strip()
        preferred_resolution = request.form.get("preferred-resolution", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO complaints 
                 (fullname, email, phone, complaint_type, incident_date, complaint_details, preferred_resolution) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (fullname, email, phone, complaint_type, incident_date, complaint_details, preferred_resolution)

        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        flash("Complaint submitted successfully!", "success")
        return redirect(url_for("complaintsform"))

if __name__ == "__main__":
    app.run(debug=True)

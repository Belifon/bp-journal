import json, os, pytz

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, g, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, classify_bp, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bloodpressure.db")




@app.route("/toggle_language")
def toggle_language():
    current_lang = session.get('language', 'tr')  # Default is Turkish
    new_lang = 'tr' if current_lang == 'en' else 'en'  # If language is Turkish changes to English, if it's English changes to Turkish 
    session['language'] = new_lang
    return redirect(request.referrer or '/')



@app.before_request
def load_language_data():
    user_lang = session.get('language', 'tr')  # Default is Turkish
    with open(f'languages/{user_lang}.json', 'r') as file:
        g.language_data = json.load(file)
    g.language_data['current_lang'] = user_lang



# Fetch all time zones
timezones = pytz.all_timezones

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.context_processor
def inject_layout_data():
    return dict(layout_data=g.language_data['layout'])


@app.context_processor
def inject_user_details():
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        if user_info:
            username = user_info[0]['username']
        else:
            username = None
    else:
        username = None
    return {'username': username}



@app.route("/")
@login_required
def index():

    # Get the current user's username
    user_id = session["user_id"]
    resultname= db.execute ("SELECT name FROM users WHERE id =?;", user_id)
    uname = resultname[0]['name']
    # Extract the username from the query result
    if uname:
        formatted_uname = uname[0].upper() + uname[1:]
    else:
        resultusername= db.execute ("SELECT username FROM users WHERE id =?;", user_id)
        uname = resultusername[0]['username']
        formatted_uname = uname[0].upper() + uname[1:]

    return render_template("index.html",uname=uname, formatted_uname=formatted_uname, data=g.language_data['index'])


@app.route("/dashboard")
@login_required
def dashboard():
    # get the user id and timezone
    user_id = session["user_id"]
    user_timezone = db.execute("SELECT timezone FROM users WHERE id = ?", user_id)[0]['timezone']
    user_tz = pytz.timezone(user_timezone)

    # Get the last 5 blood pressure readings
    recording_rows = db.execute("SELECT * FROM blood_pressure_readings WHERE user_id = ? ORDER BY reading_date DESC LIMIT 5;", user_id)
    
    # Add classification to each recording and convert time to user's timezone
    for row in recording_rows:
        row["classification"] = classify_bp(row["systolic"], row["diastolic"])
        utc_time = row["reading_date"]
        try:
            local_time = pytz.utc.localize(datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')).astimezone(user_tz)
            row["reading_date"] = local_time.strftime('%d/%m/%Y %H:%M:%S')
        except Exception as e:
            print(f"Error converting time: {e}")
            row["reading_date"] = utc_time

    # Calculate the average of just the last 5 readings
    user_avg_recording = db.execute("""
        SELECT AVG(systolic) AS avg_systolic, AVG(diastolic) AS avg_diastolic, AVG(pulse) AS avg_pulse
        FROM (
            SELECT systolic, diastolic, pulse
            FROM blood_pressure_readings
            WHERE user_id = ?
            ORDER BY reading_date DESC
            LIMIT 5
        )
    """, user_id)
    

    # Check if there are any averages calculated and handle potential None values
    if user_avg_recording:
        avg_data = {
            'avg_systolic': round(user_avg_recording[0]['avg_systolic'], 1) if user_avg_recording[0]['avg_systolic'] else '',
            'avg_diastolic': round(user_avg_recording[0]['avg_diastolic'], 1) if user_avg_recording[0]['avg_diastolic'] else '',
            'avg_pulse': round(user_avg_recording[0]['avg_pulse'], 1) if user_avg_recording[0]['avg_pulse'] else ''
        }
    else:
        avg_data = {'avg_systolic': 'N/A', 'avg_diastolic': 'N/A', 'avg_pulse': 'N/A'}

    return render_template("dashboard.html", classes=g.language_data['classes'], data=g.language_data['dashboard'], last5reading=recording_rows, user_id=user_id, user_avg_recording=[avg_data])


@app.route("/history")
@login_required
def history():
    # Get user id and timezone information
    user_id = session["user_id"]
    user_timezone = db.execute("SELECT timezone FROM users WHERE id = ?", user_id)[0]['timezone']
    user_tz = pytz.timezone(user_timezone)

    #Show history of blood pressure recordings
    recording_rows = db.execute("SELECT * FROM blood_pressure_readings WHERE user_id = ? ORDER BY reading_date DESC;", user_id)

    # Convert time to user's timezone
    for row in recording_rows:
        utc_time = row["reading_date"]
        try:
            local_time = pytz.utc.localize(datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')).astimezone(user_tz)
            row["reading_date"] = local_time.strftime('%d/%m/%Y %H:%M:%S')
        except Exception as e:
            print(f"Error converting time for row {row}: {e}")
            row["reading_date"] = utc_time # fallback to the original time if conversion fails
            

    return render_template("history.html", history=recording_rows, data=g.language_data['history'])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", data=g.language_data['login'])


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    user_time = db.execute("SELECT timezone FROM users WHERE id = ?", user_id)[0]

    if request.method == "POST":
        if "update_name" in request.form:  # Check if the name update button was clicked
            name = request.form.get("name")
            db.execute("UPDATE users SET name = ? WHERE id = ?", name, user_id)

        elif "update_timezone" in request.form:  # Check if the timezone update button was clicked
            timezone = request.form.get("timezone")
            db.execute("UPDATE users SET timezone = ? WHERE id = ?", timezone, user_id)

        elif "update_password" in request.form:  # Check if the password update button was clicked
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            if password != confirmation:
                return apology("passwords should match", 400)
            hashed_password = generate_password_hash(password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed_password, user_id)

        return redirect("/profile")

    else:
        user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
        return render_template("profile.html", user_data=user_data, data=g.language_data['profile'], timezones=timezones, user_time=user_time)



@app.route("/record", methods=["GET", "POST"])
@login_required
def record():
    # Record blood pressure reading

    if request.method == "POST":
        # Get the systolic blood pressure recording and check its validity
        systolic = request.form.get("systolic")
        try:
            systolic = int(systolic)
        except ValueError:
            return apology("systolic blood pressure should be a number", 400)

        # Get the diastolic blood pressure recording and check its validity
        diastolic = request.form.get("diastolic")
        try:
            diastolic = int(diastolic)
        except ValueError:
            return apology("diastolic blood pressure should be a number", 400)

        # Get the pulse recording and check its validity
        pulse = request.form.get("pulse")
        try:
            pulse = int(pulse)
        except ValueError:
            return apology("pulse rate should be a number", 400)

        # Get the note for the recording
        notes = request.form.get("notes")

        # Get user info log blood pressure reading to blood_pressure_recordings table
        user_id = session["user_id"] 
        user_timezone = db.execute("SELECT timezone FROM users WHERE id = ?", user_id)[0]['timezone']
        user_tz = pytz.timezone(user_timezone)

        # Get the current time in the user's timezone
        user_time = datetime.now(user_tz)
        user_time_gmt = user_time.astimezone(pytz.utc) # Convert to UTC

        db.execute("INSERT INTO blood_pressure_readings (user_id, systolic, diastolic, pulse, notes, reading_date) VALUES (?, ?, ?, ?, ?, ?)", user_id, systolic, diastolic, pulse, notes, user_time_gmt);

        """ Redirect user to their dashboard"""
        return redirect("/dashboard")

    # User reached route via GET
    else:
        return render_template("record.html", data=g.language_data['record'])



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username, password and confirmation were submitted and both passwords match
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must provide password", 400)
        elif password != confirmation:
            return apology("passwords should match", 400)

        # Ensure username does not already exist in the database
        username_exists = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if username_exists:
            return apology("username is not available", 400)

        # Register user info to database
        hashed_password = generate_password_hash(password)
        name = ""
        zone = "Turkey"
        db.execute("INSERT INTO users (username, hash, name, timezone) VALUES (?, ?, ?, ?);", username, hashed_password, name, zone)
        user_rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Remember which user has logged in
        session["user_id"] = user_rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", data=g.language_data['register'])


@app.route("/resources")
@login_required
def resources():
    user_id = session["user_id"]
    return render_template("resources.html", user_id=user_id, data=g.language_data['resources'])
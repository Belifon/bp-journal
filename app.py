import json, os, pytz

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# Import custom helper functions from helpers.py
from helpers import apology, classify_bp, login_required

# Configure application
app = Flask(__name__)

# Configure and initialize session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bloodpressure.db")

# Fetch all time zones, get a list of all time zones
timezones = pytz.all_timezones


@app.before_request
def load_language_data():

    # Default language to Turkish if not set
    if 'language' not in session:
        session['language'] = 'tr'

    # Load language data before each request, open and read the appropriate language file
    user_lang = session['language']
    with open(f'languages/{user_lang}.json', 'r') as file:
        g.language_data = json.load(file)

    # Store current language in global variable
    g.language_data['current_lang'] = user_lang 


@app.after_request
def after_request(response):

    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.context_processor
def inject_layout_data():

    # Provide layout data to all templates
    return dict(layout_data=g.language_data['layout'])


# Inject username into templates
@app.context_processor
def inject_user_details():
    
    # Check if the user is logged in, if logged in query user info from database using ID
    if 'user_id' in session: 
        user_id = session['user_id']
        user_info = db.execute("SELECT username FROM users WHERE id = ?", user_id) 
    
        # If user info found, get username
        if user_info: 
            username = user_info[0]['username']
    
        # If user info not found, set username to None
        else:
            username = None
    
    # If not logged in, set username to None
    else:
        username = None
    
    # Return username
    return {'username': username}


@app.route("/")
@login_required
def index():

    # Get the user ID from session, query the database for user's name
    user_id = session["user_id"]
    resultname= db.execute ("SELECT name FROM users WHERE id =?;", user_id)
    uname = resultname[0]['name']
    
    # If found extract the user's name from the query result and capitalize the first letter
    if uname:
        formatted_uname = uname[0].upper() + uname[1:]
    
    # If the name is not available, capitalize and use the username instead
    else:
        resultusername= db.execute ("SELECT username FROM users WHERE id =?;", user_id)
        uname = resultusername[0]['username']
        formatted_uname = uname[0].upper() + uname[1:]
    
    # Render the index page with the user's name and formatted name
    return render_template("index.html",uname=uname, formatted_uname=formatted_uname, data=g.language_data['index'])


@app.route("/dashboard")
@login_required
def dashboard():

    # Get the user ID and timezone, convert timezone to pytz timezone
    user_id = session["user_id"]
    user_timezone = db.execute("SELECT timezone FROM users WHERE id = ?", user_id)[0]['timezone']
    user_tz = pytz.timezone(user_timezone) 

    # Get the last 5 blood pressure readings
    recording_rows = db.execute("SELECT * FROM blood_pressure_readings WHERE user_id = ? ORDER BY reading_date DESC LIMIT 5;", user_id)
    
    # Add classification to each recording and convert time to user's timezone
    for row in recording_rows:

        # Add classification to each recording
        row["classification"] = classify_bp(row["systolic"], row["diastolic"])

        # Get the reading date from the database
        utc_time = row["reading_date"]

        # Convert reading date to local time and format date
        try:
            local_time = pytz.utc.localize(datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')).astimezone(user_tz)
            row["reading_date"] = local_time.strftime('%d/%m/%Y %H:%M:%S')
        
        # Fallback to the original time if conversion fails
        except Exception:
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
    
    # If averaging was successful, round the values for simplicity
    if user_avg_recording:
        avg_data = {
            'avg_systolic': round(user_avg_recording[0]['avg_systolic'], 1) if user_avg_recording[0]['avg_systolic'] else '',
            'avg_diastolic': round(user_avg_recording[0]['avg_diastolic'], 1) if user_avg_recording[0]['avg_diastolic'] else '',
            'avg_pulse': round(user_avg_recording[0]['avg_pulse'], 1) if user_avg_recording[0]['avg_pulse'] else ''
        }

    # If averaging was not successful set average values to 'N/A'
    else:
        avg_data = {'avg_systolic': 'N/A', 'avg_diastolic': 'N/A', 'avg_pulse': 'N/A'}

    # Render dashboard with user data
    return render_template("dashboard.html", classes=g.language_data['classes'], data=g.language_data['dashboard'], last5reading=recording_rows, user_id=user_id, user_avg_recording=[avg_data])


# Define the datetimeformat filter
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%dT%H:%M:%S'):
    if value is None:
        return ""
    try:
        if isinstance(value, str):
            # Try ISO 8601 format first
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        else:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        # Fallback to original format if the above fails
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return value.strftime(format)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    record = db.execute("SELECT * FROM blood_pressure_readings WHERE id = ?", id)[0]
    data=g.language_data['edit']

    if request.method == "POST":
        print("POST request received in edit route")  # Debugging statement
        try:
            systolic = request.form['systolic']
            diastolic = request.form['diastolic']
            pulse = request.form['pulse']
            timestamp = request.form['timestamp']
            notes = request.form['notes']

            # Ensure the timestamp is correctly formatted before storing it
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

            db.execute("UPDATE blood_pressure_readings SET systolic = ?, diastolic = ?, pulse = ?, reading_date = ?, notes = ? WHERE id = ?", systolic, diastolic, pulse, timestamp, notes, id)
            flash(data['editSuccess'], 'success')
            return redirect("/history")
        except Exception as e:
            flash(f"{data['editFail']} {e}", 'danger')
            return redirect(url_for('edit', id=id))

    # Render history with user data
    return render_template("edit.html", record=record, data=g.language_data['edit'])


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():

    # User reached route via POST
    if request.method == "POST":

        # If edit record button was clicked, redirect user to edit.html page
        if "edit_record" in request.form:  
            record_id = request.form.get("record_id")
            return redirect(url_for('edit', id=record_id))
        
        # If the remove record button was clicked, remove data from database
        elif "remove_record" in request.form:
            record_id = request.form.get("record_id")
            db.execute("DELETE FROM blood_pressure_readings WHERE id = ?", record_id)
            return redirect("/history")

        
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get user id and timezone information, convert to pytz timezone
        user_id = session["user_id"]
        user_timezone = db.execute("SELECT timezone FROM users WHERE id = ?", user_id)[0]['timezone']
        user_tz = pytz.timezone(user_timezone)

        # Get all blood pressure recordings for the user
        recording_rows = db.execute("SELECT * FROM blood_pressure_readings WHERE user_id = ? ORDER BY reading_date DESC;", user_id)

        # Add classification to each recording and convert time to user's timezone
        for row in recording_rows:

            # Add classification to each recording
            row["classification"] = classify_bp(row["systolic"], row["diastolic"])

            # Get the reading date from the database
            utc_time = row["reading_date"]

            # Convert reading date to local time and format date
            try:
                local_time = pytz.utc.localize(datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')).astimezone(user_tz)
                row["reading_date"] = local_time.strftime('%d/%m/%Y %H:%M:%S')
            
            # Fallback to the original time if conversion fails
            except Exception:
                row["reading_date"] = utc_time

    # Render history with user data
    return render_template("history.html", classes=g.language_data['classes'], history=recording_rows, data=g.language_data['history'])


@app.route("/login", methods=["GET", "POST"])
def login():

    # Preserve language preference before clearing session
    current_lang = session.get('language', 'tr')

    # Forget any session (user_id) info but keep the language preference
    session.clear()
    session['language'] = current_lang

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must_provide_username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must_provide_password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid_username_password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to index page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", data=g.language_data['login'])


@app.route("/logout")
def logout():
    
    # Preserve language preference before clearing session
    current_lang = session.get('language', 'tr')

    # Forget any session (user_id) info but keep the language preference
    session.clear()
    session['language'] = current_lang

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    # Get user info and timezone
    user_id = session["user_id"]
    user_time = db.execute("SELECT timezone FROM users WHERE id = ?", user_id)[0]

    # Get language data for flashing success and fail messages
    data=g.language_data['profile']

    # User reached route via POST
    if request.method == "POST":
        
        # If the update name button was clicked, get new name from form, update name in database
        if "update_name" in request.form:  
            name = request.form.get("name")
            try:
                db.execute("UPDATE users SET name = ? WHERE id = ?", name, user_id)
                flash(data['editNameSuccess'], 'success')
            except Exception as e:
                flash(f"{data['editFail']} {e}", 'danger')
                return redirect("/profile")
            

        # If the update timezone button was clicked, get new timezone from form, update timezone in database
        elif "update_timezone" in request.form:
            try:
                timezone = request.form.get("timezone")
                db.execute("UPDATE users SET timezone = ? WHERE id = ?", timezone, user_id)
                flash(data['editTimezoneSuccess'], 'success')
            except Exception as e:
                flash(f"{data['editFail']} {e}", 'danger')
                return redirect("/profile")

        # If the update password button was clicked, get new password and password confirmation from form
        elif "update_password" in request.form: 
            try:
                password = request.form.get("password")
                confirmation = request.form.get("confirmation")

                # If password and confirmation don't match, inform user and don't update database
                if password != confirmation:
                    return apology("passwords_should_match", 400)

                # Hash new password
                hashed_password = generate_password_hash(password)

                # Update password in database
                db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed_password, user_id)
                flash(data['editPasswordSuccess'], 'success')
            except Exception as e:
                flash(f"{data['editFail']} {e}", 'danger')
                return redirect("/profile")
            
        # Return user to profile page
        return redirect("/profile")

    # User reached route via GET get user data from database and render profile page
    else:
        user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
        return render_template("profile.html", user_data=user_data, data=g.language_data['profile'], timezones=timezones, user_time=user_time)



@app.route("/record", methods=["GET", "POST"])
@login_required
def record():
    
    # User reached route via POST
    if request.method == "POST":

        # Get the systolic blood pressure recording, check its validity and inform user if not valid
        systolic = request.form.get("systolic")
        try:
            systolic = int(systolic)
        except ValueError:
            return apology("systolic_bp_should_be_a_number", 400)

        # Get the diastolic blood pressure recording and check its validity and inform user if not valid
        diastolic = request.form.get("diastolic")
        try:
            diastolic = int(diastolic)
        except ValueError:
            return apology("diastolic_bp_should_be_a_number", 400)

        # Get the pulse recording and check its validity and inform user if not valid
        pulse = request.form.get("pulse")
        try:
            pulse = int(pulse)
        except ValueError:
            return apology("pulse_rate_should_be_a_number", 400)

        # Get the note for the recording
        notes = request.form.get("notes")

        # Get user info and timezone
        user_id = session["user_id"] 
        user_timezone = db.execute("SELECT timezone FROM users WHERE id = ?", user_id)[0]['timezone']
        user_tz = pytz.timezone(user_timezone)

        # Get the current time in the user's timezone, convert to UTC
        user_time = datetime.now(user_tz)
        user_time_gmt = user_time.astimezone(pytz.utc)

        # Insert reading into database
        db.execute("INSERT INTO blood_pressure_readings (user_id, systolic, diastolic, pulse, notes, reading_date) VALUES (?, ?, ?, ?, ?, ?)", user_id, systolic, diastolic, pulse, notes, user_time_gmt);

        # Redirect user to their dashboard
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
            return apology("must_provide_username", 400)
        elif not password:
            return apology("must_provide_password", 400)
        elif not confirmation:
            return apology("must_provide_password", 400)
        elif password != confirmation:
            return apology("passwords_should_match", 400)

        # Ensure username does not already exist in the database
        username_exists = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if username_exists:
            return apology("username_not_available", 400)

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

    # Get user ID and render resources page
    user_id = session["user_id"]
    return render_template("resources.html", user_id=user_id, data=g.language_data['resources'])

@app.route("/toggle_language")
def toggle_language():
    current_lang = session.get('language', 'tr')  # Get current language from session, default to Turkish
    new_lang = 'tr' if current_lang == 'en' else 'en'  # Toggle language between Turkish and English 
    session['language'] = new_lang # Save new language to session
    return redirect(request.referrer or '/') # Redirect back to the previous page
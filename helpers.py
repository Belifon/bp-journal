import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import g, redirect, render_template, session
from functools import wraps


def apology(message_key, code=400):
    
    # Print message and code to check if the function is called correctly TO BE DELETED
    print(f"Apology called with message: {message_key} and code: {code}")

    
    def escape(s):

        # Escape special characters. https://github.com/jacebrowning/memegen#special-characters
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"), ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    
    # Retrieve the translated message using the message_key
    message = g.language_data['errors'].get(message_key, message_key)
    top_message = escape(message)
    bottom_message = str(code)
    img_src = f"http://memegen.link/custom/{urllib.parse.quote(top_message)}/{urllib.parse.quote(bottom_message)}.jpeg?alt=https://i.imgur.com/Z6WSXng.jpeg&width=400"
    

    return render_template("apology.html", top=top_message, bottom=bottom_message, img_src=img_src), code
    # return render_template("apology.html", top=code, bottom=escape(message)), code


# Classify blood pressure based on systolic and diastolic values. Source: https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings
def classify_bp(systolic, diastolic):
    
    # Normal blood pressure
    if systolic < 120 and diastolic < 80:
        return "Normal"
    
    # Elevated BP
    elif 120 <= systolic < 130 and diastolic < 80:
        return "Elevated"

    # Hypertension stage 1
    elif 130 <= systolic < 140 or 80 <= diastolic < 90:
        return "High1"
    
    # Hypertension stage 2
    elif 140 <= systolic or 90 <= diastolic:
        return "High2"
    
    # Hypertensive crisis
    else:
        return "Crisis"


def login_required(f):
    # Decorate routes to require login. http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/, imported from CS50x Finance
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        # Check if user is logged in and redirect to login page if not logged in
        if session.get("user_id") is None:
            return redirect("/login")
        
        # Call the original function if logged in
        return f(*args, **kwargs)
    return decorated_function
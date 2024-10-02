from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os
import json
import threading
import time
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Beispiel für Benutzerdaten (in einer realen App solltest du eine Datenbank verwenden)
users = {'admin': 'password'}

# Funktion zum Abrufen der Wetterdaten
def get_weather_data():
    api_key = os.getenv('OPENWEATHER_API_KEY')  # OpenWeather API-Key
    location = os.getenv('LOCATION')  # Ort
    url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&lang=de&units=metric'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Gib die Wetterdaten als JSON zurück
    else:
        return None

def check_weather():
    weather_api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": os.getenv('LOCATION'),  # Ort, den du überwachen möchtest
        "appid": os.getenv('OPENWEATHER_API_KEY'),  # OpenWeather API-Key
        "lang": "de",  # Sprache auf Deutsch
        "units": "metric"  # Einheiten auf metrisch
    }
    response = requests.get(weather_api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        # Prüfe auf extreme Wetterbedingungen
        if 'weather' in data and len(data['weather']) > 0:
            if "extreme" in data["weather"][0]["description"]:
                send_gotify_alert("Extreme Unwetterstufe in Überherrn! Sofort handeln.")
    else:
        print(f"Fehler bei der API-Anfrage: {response.status_code} - {response.text}")

def send_gotify_alert(message):
    gotify_url = os.getenv('GOTIFY_URL')  # URL zu Gotify
    headers = {
        "Content-Type": "application/json",
        "X-Gotify-Key": os.getenv('GOTIFY_API_KEY')  # Gotify API-Key
    }
    payload = {
        "title": "Unwetterwarnung",
        "message": message,
        "priority": 10
    }
    requests.post(gotify_url, headers=headers, data=json.dumps(payload))

def weather_monitor():
    while True:
        check_weather()
        time.sleep(600)  # Überprüfe alle 10 Minuten

# Starte den Wetterüberwachungs-Thread
threading.Thread(target=weather_monitor, daemon=True).start()

# Login-Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Dashboard-Route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    weather_data = get_weather_data()
    return render_template('dashboard.html', weather=weather_data)

# Route für Testalarm
@app.route('/send_test_alert')
def send_test_alert():
    send_gotify_alert("Dies ist ein Testalarm aus der Wetter-App!")
    return redirect(url_for('dashboard'))

# Route für Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

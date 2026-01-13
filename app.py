import random
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import sqlite3
import os
from datetime import datetime
app = Flask(__name__)
app.secret_key = "nachhilfe_geheimnis_123"

# Datenbank initialisieren
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Lehrer-Tabelle
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    # Unterrichts-Logs
    c.execute('''CREATE TABLE IF NOT EXISTS lesson_logs 
                 (id INTEGER PRIMARY KEY, teacher TEXT, student TEXT, exercise TEXT, timestamp TEXT)''')
    # Beispiel-Lehrer anlegen (nur wenn leer)
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES ('admin', 'start123')")
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['user'] = username
        return redirect(url_for('dashboard'))
    return "Login fehlgeschlagen! <a href='/'>Zurück</a>"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', teacher=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# --- ÜBUNGEN ---

@app.route('/exercise/articles')
def exercise_articles():
    if 'user' not in session: return redirect(url_for('index'))
    student_name = session.get('student_name', 'Unbekannter Schueler')
    return render_template('exercises/articles.html', student_name=student_name)

@app.route('/start_lesson', methods=['POST'])
def start_lesson():
    data = request.json
    teacher = session['user']
    student = data.get('student')
    exercise = data.get('exercise')
    session['student_name'] = student
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO lesson_logs (teacher, student, exercise, timestamp) VALUES (?, ?, ?, ?)",
              (teacher, student, exercise, now))
    conn.commit()
    conn.close()
    return jsonify({"status": "logged"})

# Neue Route: Gibt alle verfügbaren Kategorien (Dateinamen ohne .json) zurück
@app.route('/get_categories', methods=['GET'])
def get_categories():
    files = [f.replace('.json', '') for f in os.listdir("categories/articles") if f.endswith('.json')]
    return jsonify(files)

@app.route('/get_word', methods=['GET'])
def get_word():
    category = request.args.get('category')
    file_path = os.path.join("categories/articles", f"{category}.json")
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Kategorie nicht gefunden"}), 404
        
    with open(file_path, 'r', encoding='utf-8') as f:
        words = json.load(f)
    
    return jsonify(random.choice(words))

@app.route('/log_error', methods=['POST'])
def log_error():
    data = request.json
    session_name = data.get('session_name', 'N/A')
    exercise = data.get('exercise', 'N/A')
    category = data.get('category', 'N/A')
    wrong_word = data.get('word', 'N/A')
    wrong_article = data.get('wrong_article', 'N/A')
    score_right = data.get('score_right', 'N/A')
    score_wrong = data.get('score_wrong', 'N/A')
    
    time = datetime.now().strftime("%H:%M:%S")
    # Log-Format inkl. Kategorie
    log_entry = f"{time} | Übung: {exercise} | Kat: {category} | falsche Antwort: {wrong_article} | Wort: {wrong_word}\n | Right: {score_right}\n | Wrong: {score_wrong} "

    now = datetime.now().strftime("%Y_%m_%d")
    filename = f"./logs/{session_name}/log_{now}.txt"
    output_file = Path(filename)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    return jsonify({"status": "logged"})


@app.route('/admin/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    # Sicherheitscheck: Nur der Haupt-Admin darf das
    if 'user' not in session or session['user'] != 'admin':
        return "Zugriff verweigert! Nur der Admin kann Lehrer anlegen."

    if request.method == 'POST':
        new_name = request.form.get('new_username')
        new_pass = request.form.get('new_password')

        if new_name and new_pass:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_name, new_pass))
                conn.commit()
                message = f"Lehrer '{new_name}' wurde erfolgreich angelegt!"
            except sqlite3.IntegrityError:
                message = "Fehler: Dieser Benutzername existiert bereits."
            conn.close()
            return f"{message} <a href='/dashboard'>Zurück zum Dashboard</a>"

    return render_template('admin/add_teacher.html')

@app.route('/admin/logs')
def view_logs():
    # Sicherheitscheck: Nur der Admin darf die Protokolle sehen
    if 'user' not in session or session['user'] != 'admin':
        return "Zugriff verweigert!"

    conn = sqlite3.connect('database.db')
    # row_factory erlaubt uns den Zugriff über Spaltennamen (wie ein Dictionary)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM lesson_logs ORDER BY id DESC")
    logs = c.fetchall()
    conn.close()

    return render_template('admin/view_logs.html', logs=logs)

@app.route('/get_adjective_categories')
def get_adjective_categories():
    files = os.listdir('categories/adjectiv_declension/')
    categories = [f.replace('.json', '')
                  for f in files if f.endswith('.json')]
    return jsonify(categories)


@app.route('/get_adjective_exercise')
def get_adjective_exercise():
    category = request.args.get('category')
    filepath = os.path.join('categories/adjectiv_declension', f"{category}.json")

    if not os.path.exists(filepath):
        return jsonify({"error": "Datei nicht gefunden"}), 404

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(random.choice(data))

@app.route('/exercise/adjective_declension')
def adjective_declension():
    # Sicherheitscheck: Ist ein Lehrer eingeloggt und ein Schüler aktiv?
    if 'user' not in session or 'student_name' not in session:
        return redirect(url_for('dashboard'))

    # Kategorie aus der URL holen (Standard: 'allgemein')
    category = request.args.get('category', 'allgemein')

    return render_template('exercises/adjective.html',
                           student_name=session['student_name'],
                           category=category)

@app.route('/get_students')
def get_students():
    l = os.listdir('logs/')
    l.sort()
    return jsonify(l)

@app.route('/exercise/prepositions')
def prepositions():
    # Sicherheitscheck: Ist ein Lehrer eingeloggt und ein Schüler aktiv?
    if 'user' not in session or 'student_name' not in session:
        return redirect(url_for('dashboard'))

    # Kategorie aus der URL holen (Standard: 'allgemein')
    category = request.args.get('category', 'allgemein')

    return render_template('exercises/prepositions.html',
                           student_name=session['student_name'],
                           category=category)


@app.route('/get_preposition_categories')
def get_preposition_categories():
    files = os.listdir('categories/prepositions/')
    # Sucht nach Dateien wie prepositions_lokal.json
    categories = [f.replace('.json', '')
                  for f in files if f.endswith('.json')]
    return jsonify(categories)

@app.route('/get_preposition_exercise')
def get_preposition_exercise():
    category = request.args.get('category')
    filepath = os.path.join('categories/prepositions', f"{category}.json")
    if not os.path.exists(filepath): return jsonify({"error": "Nicht gefunden"}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(random.choice(data))



@app.route('/exercise/past_tense')
def past_tense():
    # Sicherheitscheck: Ist ein Lehrer eingeloggt und ein Schüler aktiv?
    if 'user' not in session or 'student_name' not in session:
        return redirect(url_for('dashboard'))

    # Kategorie aus der URL holen (Standard: 'allgemein')
    category = request.args.get('category', 'allgemein')

    return render_template('exercises/past_tense.html',
                           student_name=session['student_name'],
                           category=category)


@app.route('/get_past_tense_categories')
def get_past_tense_categories():
    files = os.listdir('categories/past_tense/')
    categories = [f.replace('.json', '')
                  for f in files if f.endswith('.json')]
    return jsonify(categories)

@app.route('/get_past_tense_exercise')
def get_past_tense_exercise():
    category = request.args.get('category')
    filepath = os.path.join('categories/past_tense', f"{category}.json")
    if not os.path.exists(filepath): return jsonify({"error": "Nicht gefunden"}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(random.choice(data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
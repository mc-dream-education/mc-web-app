import random
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import sqlite3
import os
from datetime import datetime
app = Flask(__name__)
app.secret_key = "nachhilfe_geheimnis_123"
DATABASE = 'database.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # 1. Lehrer/User-Tabelle
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY,
                     username
                     TEXT,
                     password
                     TEXT
                 )''')

    # 2. Erweiterte Unterrichts-Logs
    # Wir speichern: Wer (student), in welchem Text (source_file), welches Wort (error_word)
    c.execute('''CREATE TABLE IF NOT EXISTS lesson_logs
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     teacher
                     TEXT,
                     student
                     TEXT,
                     exercise_type
                     TEXT,
                     source_file
                     TEXT,
                     error_word
                     TEXT,
                     timestamp
                     DATETIME
                     DEFAULT
                     CURRENT_TIMESTAMP
                 )''')

    # Beispiel-Lehrer anlegen
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES ('admin', 'start123')")

    conn.commit()
    conn.close()
    print("Datenbank erfolgreich initialisiert.")

init_db()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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


@app.route('/exercise/memorize/<filename>')
def exercise_memorize(filename):
    # Wir holen den Namen aus der Session (User-Eingabe beim Start des Portals)
    student_name = session.get('student_name')
    if not student_name:
        return "Kein Schüler ausgewählt", 403

    file_path = os.path.join('categories/memorize', f'{filename}.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = get_db_connection()
    # KORREKTUR: Spaltenname 'student' statt 'student_name'
    past_errors = conn.execute('''
        SELECT DISTINCT error_word 
        FROM lesson_logs 
        WHERE student = ? AND source_file = ?
    ''', (student_name, filename)).fetchall()
    conn.close()

    error_list = [row['error_word'] for row in past_errors]

    return render_template('exercises/memorize.html',
                           data=data,
                           filename=filename,
                           past_errors=error_list)


@app.route('/exercise/memorize')
def list_memorize_exercises():
    student_name = session.get('student_name')
    if not student_name:
        return redirect(url_for('index'))  # Oder wo auch immer dein Login ist

    base_path = 'categories/memorize'
    exercises = []

    # Scanne alle Dateien im Ordner
    if os.path.exists(base_path):
        for filename in os.listdir(base_path):
            if filename.endswith('.json'):
                file_id = filename.replace('.json', '')

                # Titel aus der JSON lesen für die Anzeige
                try:
                    with open(os.path.join(base_path, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        exercises.append({
                            'id': file_id,
                            'title': data.get('title', file_id),
                            'preview': data.get('text', '')[:60] + "..."  # Kurze Vorschau
                        })
                except Exception as e:
                    print(f"Fehler beim Laden von {filename}: {e}")

    return render_template('exercises/memorize_list.html', exercises=exercises)

# Beispiel für die bestehende log_error Route (falls noch nicht voll implementiert)
@app.route('/log_error_memory', methods=['POST'])
def log_error_memory():
    req_data = request.json
    student_name = session.get('student_name')

    conn = get_db_connection()
    conn.execute('''
                 INSERT INTO lesson_logs (student_name, source_file, error_word, timestamp)
                 VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                 ''', (student_name, req_data['filename'], req_data['word']))
    conn.commit()
    conn.close()
    return jsonify({"status": "logged"})


@app.route('/exercise/das-dass')
def exercise_das_dass():
    # Sicherheitscheck: Ist ein Schüler angemeldet?
    if 'student_name' not in session:
        return redirect(url_for('login'))  # Oder entsprechende Route

    json_path = os.path.join(app.root_path, 'categories/das_dass', 'das_dass.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        questions = []

    return render_template(
        'exercises/das_dass.html',
        questions=questions,
        student_name=session.get('student_name')
    )


@app.route('/exercise/satzbau')
def exercise_syntax():
    # Pfad zum Kategorien-Ordner
    category_path = os.path.join(app.root_path, 'categories/satzbau')

    # Beispiel: Wir suchen nach einer Datei namens 'syntax_sentences.json'
    # Alternativ: Alle JSONs im Ordner listen und eine zufällig wählen
    try:
        with open(os.path.join(category_path, 'syntax_sentences.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Wähle einen zufälligen Beispielsatz aus der Liste in der JSON
            # Ich gehe davon aus, dass die JSON ein Array von Objekten enthält
            random_sentence = random.choice(data['sentences'])
    except (FileNotFoundError, IndexError, KeyError):
        # Fallback oder Fehlermeldung
        return "Fehler beim Laden der Übungsdaten.", 404

    # Bestimme zufällig das Ziel: Hauptsatz (HS) oder Gliedsatz (GS)
    target_type = random.choice(['HS', 'GS'])
    target_label = "den Hauptsatz" if target_type == "HS" else "den Gliedsatz"

    return render_template('exercises/syntax_exercise.html',
                           sentence_parts=random_sentence['sentence_parts'],
                           target_type=target_type,
                           target_label=target_label,
                           full_sentence=" ".join([p['text'] for p in random_sentence['sentence_parts']]))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import os
import sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

ADMIN_PASSWORD_HASH = generate_password_hash("brins23")

# DEFINISCI PRIMA I PERCORSI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'public', 'uploads')
DB_DIR = os.path.join(BASE_DIR, 'db')
DB_PATH = os.path.join(DB_DIR, 'dedications.db')
print("Percorso database:", DB_PATH)
print("Percorso upload:", UPLOAD_FOLDER)

# CREA L'APP FLASK
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'public'), template_folder=os.path.join(BASE_DIR, 'public'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'

def ensure_db():
    """Crea la tabella dedications se non esiste."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS dedications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dedication TEXT NOT NULL,
                photo TEXT
            )
        ''')
        conn.commit()

ensure_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    dedication = request.form.get('dedication')
    photo = request.files.get('photo')
    filename = ""
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            filename = f"{base}_{counter}{ext}"
            counter += 1
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO dedications (name, dedication, photo) VALUES (?, ?, ?)", (name, dedication, filename))
        conn.commit()
        print("DEDICA INSERITA:", name, dedication, filename)
    return redirect(url_for('submitted'))

@app.route('/submitted')
def submitted():
    return app.send_static_file('submitted.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/dedications')
def get_dedications():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT name, dedication, photo FROM dedications")
        dedications = [{'name': row[0], 'dedication': row[1], 'photo': row[2]} for row in c.fetchall()]
    return jsonify(dedications)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Rimuovi la richiesta dell'email, controlla solo la password
        password = request.form.get('password')
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect('/stories')
        else:
            return render_template('login.html', error="Credenziali errate")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

@app.route('/stories')
def stories():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('stories.html')

if __name__ == '__main__':
    app.run(debug=True)
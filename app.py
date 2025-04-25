import sqlite3
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable credentials for cross-origin requests
app.secret_key = 'e9b1c3f4a8d9e7f2b6c1d4e5f7a8b9c0'  # Replace with your generated key

# SQLite DB config
DB_PATH = 'game_site.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)  # Allow multithreading
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    conn.execute("PRAGMA journal_mode=WAL;")  # Enable Write-Ahead Logging
    return conn

otp_store = {}  # Temporary store for OTPs

# --------------------------------------
# USER AUTHENTICATION ROUTES
# --------------------------------------

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    otp = random.randint(100000, 999999)
    otp_store[email] = otp

    try:
        # Send OTP via Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.set_debuglevel(1)  # Enable debug output for SMTP
            server.starttls()
            server.login('brainbite09@gmail.com', 'kfnc xyra ecod pnsd')  # Replace with your App Password
            message = f"Subject: Your OTP\n\n bhosdike otp ha daal na gand me dalega kya isse Your OTP is {otp}."
            server.sendmail('brainbite09@gmail.com', email, message)
            print(f"OTP {otp} sent to {email}")  # Debug log to confirm email was sent

        return jsonify({'success': True, 'message': 'OTP sent to your email(please check spam folder also).'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error sending OTP: {str(e)}'})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    otp = data.get('otp')

    if otp_store.get(email) != int(otp):
        return jsonify({'success': False, 'message': 'Invalid OTP.'})

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (email, password))
        conn.commit()
        cur.close()
        conn.close()
        otp_store.pop(email, None)  # Remove OTP after successful signup
        return jsonify({'success': True, 'message': 'Signup successful! Please login.'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '⚠️ Email already exists.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and check_password_hash(row[0], password):
        session['username'] = username
        return jsonify({'success': True, 'message': 'Login successful!'})
    return jsonify({'success': False, 'message': '❌ Invalid username or password'})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('secret', None)
    return jsonify({'message': 'Logged out successfully'})

@app.route('/signup-page')
def signup_page():
    return send_from_directory('templets', 'signup.html')

# --------------------------------------
# GAME LOGIC ROUTES
# --------------------------------------

@app.route('/start-game', methods=['GET'])
def start_game():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    session['secret'] = random.randint(1000, 9999)
    print(f"Secret Number (Debugging): {session['secret']}")
    return jsonify({"message": "Game Started! Enter a 4-digit number."})

@app.route('/guess', methods=['POST'])
def guess():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    guess_number = data.get('guess')

    if not guess_number or not guess_number.isdigit() or len(guess_number) != 4:
        return jsonify({"result": "invalid", "message": "⚠️ Please enter a valid 4-digit number."})

    guess_number = int(guess_number)
    secret = session.get('secret')

    if secret is None:
        return jsonify({'message': 'No game in progress. Start the game first.'}), 400

    if guess_number == secret:
        session.pop('secret')
        return jsonify({"result": "correct", "message": "🎉 Congratulations! You won!"})
    elif guess_number > secret:
        return jsonify({"result": "retry", "message": "🔻 Too high! Try again."})
    else:
        return jsonify({"result": "retry", "message": "🔺 Too low! Try again."})

@app.route('/quit', methods=['POST'])
def quit_game():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    session.pop('secret', None)
    return jsonify({"message": "Game Over! You quit the game."})

@app.route('/')
def home():
    return send_from_directory('templets', 'index.html')  # Serve the index.html file

# --------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

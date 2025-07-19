from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ✅ Database connection
conn = sqlite3.connect("streetspeaks.db", check_same_thread=False)
cursor = conn.cursor()

# ✅ Create tables if not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    phone TEXT,
    email TEXT UNIQUE NOT NULL,
    district TEXT,
    locality TEXT,
    address TEXT,
    pincode TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    location TEXT,
    status TEXT DEFAULT 'Pending',
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS votes (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    complaint_id INTEGER,
    vote_type TEXT,
    UNIQUE(user_id, complaint_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(complaint_id) REFERENCES complaints(complaint_id)
)''')

conn.commit()

# ✅ Landing Page
@app.route('/')
def home():
    return render_template('index.html')

# ✅ Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        phone = request.form['phone']
        email = request.form['email']
        district = request.form['district']
        locality = request.form['locality']
        address = request.form['address']
        pincode = request.form['pincode']

        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        try:
            cursor.execute("""INSERT INTO users (username, password, phone, email, district, locality, address, pincode)
                              VALUES (?,?,?,?,?,?,?,?)""",
                           (username, hashed.decode('utf-8'), phone, email, district, locality, address, pincode))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already exists!"

    return render_template('2create.html')

# ✅ Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user[2].encode('utf-8')):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email or password!"

    return render_template('login.html')

# ✅ Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor.execute("SELECT locality FROM users WHERE user_id=?", (user_id,))
    locality = cursor.fetchone()[0]

    cursor.execute("""
        SELECT complaints.complaint_id, complaints.title, complaints.description, complaints.status,
               complaints.upvotes, complaints.downvotes, users.username
        FROM complaints
        JOIN users ON complaints.user_id = users.user_id
        WHERE users.locality=?
        ORDER BY complaints.upvotes DESC
    """, (locality,))
    complaints = cursor.fetchall()

    return render_template('dashboard.html', complaints=complaints, username=session['username'])

# ✅ Voting API
@app.route('/vote/<int:complaint_id>/<vote_type>', methods=['POST'])
def vote(complaint_id, vote_type):
    if 'user_id' not in session:
        return jsonify({"error": "Login required"}), 403

    user_id = session['user_id']

    cursor.execute("SELECT vote_type FROM votes WHERE user_id=? AND complaint_id=?", (user_id, complaint_id))
    existing_vote = cursor.fetchone()

    if existing_vote:
        return jsonify({"error": "You already voted!"}), 400

    if vote_type == 'up':
        cursor.execute("UPDATE complaints SET upvotes = upvotes + 1 WHERE complaint_id=?", (complaint_id,))
    elif vote_type == 'down':
        cursor.execute("UPDATE complaints SET downvotes = downvotes + 1 WHERE complaint_id=?", (complaint_id,))
    else:
        return jsonify({"error": "Invalid vote type"}), 400

    cursor.execute("INSERT INTO votes (user_id, complaint_id, vote_type) VALUES (?,?,?)",
                   (user_id, complaint_id, vote_type))
    conn.commit()

    return jsonify({"message": "Vote added successfully"}), 200

# ✅ Profile
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor.execute("SELECT username, email, phone, district, locality, address, pincode FROM users WHERE user_id=?",
                   (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT title, description, status FROM complaints WHERE user_id=?", (user_id,))
    user_complaints = cursor.fetchall()

    return render_template('profile.html', user=user, user_complaints=user_complaints)

# ✅ Upload Complaint
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        user_id = session['user_id']

        cursor.execute("INSERT INTO complaints (user_id, title, description, location) VALUES (?,?,?,?)",
                       (user_id, title, description, location))
        conn.commit()
        return redirect(url_for('dashboard'))

    return render_template('complaint.html')

# ✅ Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

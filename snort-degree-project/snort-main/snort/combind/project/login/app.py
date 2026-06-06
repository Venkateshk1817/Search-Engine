from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3, random, smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a Flask blueprint for the login system
login_blueprint = Blueprint("login", __name__, template_folder="templates", static_folder="static")

def init_db():
    conn = sqlite3.connect("login/users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    verified INTEGER DEFAULT 0,
                    otp TEXT
                )''')
    conn.commit()
    conn.close()

def send_otp(email, otp):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    
    if not sender_email or not sender_password:
        print("Email credentials not set in environment variables.")
        return
    
    subject = "Your Snort OTP Code"
    body = f"Your OTP code is: {otp}"
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Error sending email:", e)

@login_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = sqlite3.connect("login/users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            if user[4] == 0:  # Check if user is not verified
                flash("Please verify your email first", "error")
                return redirect(url_for("login.verify", username=username))
            
            session["username"] = username
            flash("Successfully logged in!", "success")
            return redirect(url_for("search.search"))
        else:
            flash("Invalid username or password", "error")
    
    return render_template("login.html")

@login_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        hashed_password = generate_password_hash(password)
        
        conn = sqlite3.connect("login/users.db")
        c = conn.cursor()
        
        try:
            c.execute("INSERT INTO users (username, email, password, otp) VALUES (?, ?, ?, ?)",
                     (username, email, hashed_password, otp))
            conn.commit()
            
            # Send OTP email
            send_otp(email, otp)
            
            flash("Registration successful! Please check your email for OTP verification.", "success")
            return redirect(url_for("login.verify", username=username))
        except sqlite3.IntegrityError:
            flash("Username or email already exists", "error")
        finally:
            conn.close()
    
    return render_template("register.html")

@login_blueprint.route("/verify/<username>", methods=["GET", "POST"])
def verify(username):
    if request.method == "POST":
        otp_entered = request.form["otp"]
        conn = sqlite3.connect("login/users.db")
        c = conn.cursor()
        c.execute("SELECT otp FROM users WHERE username = ?", (username,))
        user_otp = c.fetchone()
        
        if user_otp and user_otp[0] == otp_entered:
            c.execute("UPDATE users SET verified = 1, otp = NULL WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            flash("Email verified successfully! Please login.", "success")
            return redirect(url_for("login.login"))
        else:
            flash("Invalid OTP!", "error")
            return render_template("verify.html", username=username)
    
    return render_template("verify.html", username=username)

@login_blueprint.route("/logout")
def logout():
    session.pop("username", None)
    flash("Successfully logged out!", "success")
    return redirect(url_for("login.login"))

# Initialize database when the app starts
init_db()

from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, flash
import requests
import sqlite3
import os
from functools import wraps

search_blueprint = Blueprint('search', __name__, template_folder='templates')

# API Keys (Replace with your actual API keys)
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "8bd05715")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "cffb46a71cc245d794f72b7c8f2acacc")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function

# Database setup
def init_db(app=None):
    """Initialize the database"""
    conn = sqlite3.connect("search_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Store search history
def save_search_history(query):
    username = session.get("username")
    if not username:
        return
    conn = sqlite3.connect("search_history.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (username, query) VALUES (?, ?)", (username, query))
    conn.commit()
    conn.close()

# Get search history
def get_search_history_with_timestamps():
    username = session.get("username")
    if not username:
        return []
    conn = sqlite3.connect("search_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT query, timestamp FROM history WHERE username = ? ORDER BY id DESC LIMIT 10", (username,))
    history = cursor.fetchall()
    conn.close()
    return history

# Clear history
@search_blueprint.route("/clear_history", methods=["POST"])
@login_required
def clear_history():
    username = session.get("username")
    if not username:
        return "Unauthorized", 403
    conn = sqlite3.connect("search_history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    flash('Search history cleared successfully', 'success')
    return redirect(url_for('search.search_history'))

@search_blueprint.route("/history")
@login_required
def search_history():
    history = get_search_history_with_timestamps()
    return render_template("search_history.html", history=history)

# Wikipedia search
def search_wikipedia(query):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "summary": data.get("extract"),
                "image": data.get("thumbnail", {}).get("source")
            }
    except Exception as e:
        current_app.logger.error(f"Wikipedia search error: {str(e)}")
    return None

# OMDb (IMDb) search
def search_omdb(query):
    try:
        url = f"http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["Response"] == "True":
                return {
                    "title": data.get("Title"),
                    "year": data.get("Year"),
                    "poster": data.get("Poster"),
                    "plot": data.get("Plot")
                }
    except Exception as e:
        current_app.logger.error(f"OMDb search error: {str(e)}")
    return None

# NewsAPI search
def search_news(query):
    try:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])[:3]
            return [{
                "title": article["title"],
                "url": article["url"],
                "image": article.get("urlToImage")
            } for article in articles]
    except Exception as e:
        current_app.logger.error(f"News search error: {str(e)}")
    return []

@search_blueprint.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    username = session["username"]
    conn = sqlite3.connect("login/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    email = row[0] if row else "Not found"

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")

        # Check current password
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        stored_password = cursor.fetchone()[0]

        if stored_password != current_password:
            flash('Incorrect current password', 'error')
            conn.close()
            return render_template("profile.html", username=username, email=email)

        # Update new password
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        conn.close()
        flash('Password updated successfully!', 'success')
        return render_template("profile.html", username=username, email=email)

    conn.close()
    return render_template("profile.html", username=username, email=email)

@search_blueprint.route("/", methods=["GET", "POST"])
@login_required
def search():
    search_results = {}
    if request.method == "POST":
        query = request.form["query"].strip()
        if query:
            save_search_history(query)
            try:
                search_results = {
                    "wikipedia": search_wikipedia(query),
                    "omdb": search_omdb(query),
                    "news": search_news(query)
                }
                if not any(search_results.values()):
                    flash('No results found for your search query. Please try a different search term.', 'error')
            except Exception as e:
                current_app.logger.error(f"Search error: {str(e)}")
                flash('An error occurred while searching. Please try again later.', 'error')
    return render_template("index.html", results=search_results)

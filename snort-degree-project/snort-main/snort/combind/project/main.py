from flask import Flask, redirect, url_for, session
from login.app import login_blueprint, init_db as init_login_db
from engine.app import search_blueprint, init_db as init_search_db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY", "32a7f1f51dda2c237090b45699fac699df7e4fcca88cfb1414c8f29a453ad853")

# Register blueprints
app.register_blueprint(login_blueprint)
app.register_blueprint(search_blueprint, url_prefix="/search")

# Initialize databases
init_login_db()
init_search_db()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('search.search'))
    return redirect(url_for('login.login'))

if __name__ == '__main__':
    app.run(debug=True)

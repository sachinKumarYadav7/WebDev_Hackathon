from flask import Flask, render_template, session, redirect, request
from functools import wraps
from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Add a secret key for session management

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.admin  # replace 'login_user' with your database name
users_collection = db.user_login  # replace 'users' with your collection name

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap

@app.route('/')
def login():
    from user.models import User  # Import User class here
    user_manager = User(db)  # Create an instance of User class here
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login_user():
    from user.models import User  # Import User class here
    user_manager = User(db)  # Create an instance of User class here
    email = request.form['email']
    password = request.form['password']
    return user_manager.login()

@app.route('/home')
@login_required
def home():
    user = session.get('user')
    if user:
        user_name = user.get('name')
    else:
        user_name = None
    return render_template('home.html', user_name=user_name)

@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)

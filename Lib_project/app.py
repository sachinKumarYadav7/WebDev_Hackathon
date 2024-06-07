from flask import Flask, render_template, session, redirect, request, jsonify,url_for
from functools import wraps
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Add a secret key for session management

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

db = client.admin  # replace 'login_user' with your database name
users_collection = db.user_login  # replace 'users' with your collection name

allb = client.all_books  # replace 'login_user' with your database name
b = allb.books  # replace 'users' with your collection name

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
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login_user():
    from user.models import User  
    user_manager = User(db)  
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

@app.route('/admin_home')
@login_required
def admin_home():
    admin = session.get('admin')
    if admin:
        user_name = admin.get('name')
    else:
        user_name = None
    return render_template('admin_dash.html', user_name=user_name)

@app.route('/login')
def search():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('logged_in', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@app.route('/books')
def get_books():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    skip = (page - 1) * limit
    
    books = list(b.find().skip(skip).limit(limit))
    for book in books:
        book['_id'] = str(book['_id'])  # Convert ObjectId to string for JSON serialization
    
    return jsonify(books)

if __name__ == '__main__':
    app.run(debug=True)

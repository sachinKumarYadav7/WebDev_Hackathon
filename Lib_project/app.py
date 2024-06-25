from flask import Flask, render_template, session, redirect, request, jsonify,url_for
from functools import wraps
from pymongo import MongoClient
from flask import Flask, request, jsonify
# from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Add a secret key for session management

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

db = client.admin  # replace 'login_user' with your database name
users_collection = db.user_login  # replace 'users' with your collection name

allb = client.all_books  # replace 'login_user' with your database name
b = allb.books2  # replace 'users' with your collection name

announce = client.admin
announcements = announce.announcements

issue = client.admin
acc = client.admin
# announcements = issue.announcements

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


@app.route('/announcements', methods=['POST'])
def add_announcement():
    data = request.get_json()
    if not data or not 'announcement' in data:
        return jsonify({"error": "Invalid data"}), 400

    announcement = {
        "announcement": data['announcement'],
        "timestamp": datetime.utcnow().isoformat()
    }
    announcement_id = announce.announcements.insert_one(announcement).inserted_id
    return jsonify({"message": "Announcement added", "id": str(announcement_id)}), 201

@app.route('/announcements', methods=['GET'])
def get_announcements():
    announcements = announce.announcements.find().sort("timestamp", -1)
    return dumps(announcements), 200

@app.route('/issue_req' , methods=['POST'])
def add_issue_req():
    data = request.get_json()
    user = session.get('user')

    issue_request = {
        "Name" : user.get('name'),
        "email" : user.get('email'),
        "bookname" : data['bookname'],
        "timestamp": datetime.utcnow().isoformat()
    }

    issue_request_id = issue.issue_request.insert_one(issue_request).inserted_id
    return jsonify({"message": "issue req added", "id": str(issue_request_id)}), 201

@app.route('/loadissuereqs', methods=['GET'])
def get_requests():
    user = session.get('user')
    email = user.get('email')
    issue_requests = issue.issue_request.find({"email": email}).sort("timestamp", -1)
    return dumps(issue_requests), 200

@app.route('/loadallissuereqs', methods=['GET'])
def get_all_requests():
    issue_requests = issue.issue_request.find().sort("timestamp", -1)
    return dumps(issue_requests), 200

@app.route('/delete/<entry_id>', methods=['POST'])
def delete_entry(entry_id):
    try:
        issue.issue_request.delete_one({'_id':ObjectId(entry_id) })
        return jsonify({'status': 'success', 'message': 'Entry deleted successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/accepted' ,methods=['POST'])
def add_to_accepted():
    data = request.get_json()
    acc_request = {
        "req" : data['req'],
        "timestamp": datetime.utcnow().isoformat()
    }
    acc_request_id = acc.accepted.insert_one(acc_request).inserted_id
    return jsonify({"message": "issue req added", "id": str(acc_request_id)}), 201

@app.route('/loadaccbooks', methods=['GET'])
def get_all_issued_books():
    acc_requests = acc.accepted.find().sort("timestamp", +1)
    return dumps(acc_requests), 200

@app.route('/load_acc_by_user', methods=['GET'])
def get_acc_by_user():
    user = session.get('user')
    email = user.get('email')
    acc_by_user = acc.accepted.find({"req.email": email}).sort("req.timestamp", -1)
    return dumps(acc_by_user), 200
    
@app.route('/search' , methods = ['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')

    results = list(b.find({"title": {"$regex": query, "$options": "i"}}))

    for book in results:
        book['_id'] = str(book['_id'])


    return jsonify(results)

@app.route('/search_by_genre_and_dept', methods=['POST'])
def searchbydeptngenre():
    data = request.get_json()
    dept = data.get('dept', '')
    genre = data.get('genre', '')
 
    query = {}
    if genre :
        query["genre"] = {"$regex": genre, "$options": "i"}
    if dept:
        query["department"] = {"$regex": dept, "$options": "i"}
 
    results = list(b.find(query))
    
    for book in results:
        book['_id'] = str(book['_id'])

    return jsonify(results)



if __name__ == '__main__':
    app.run(debug=True)

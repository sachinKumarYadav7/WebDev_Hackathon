from flask import Flask, render_template, session, redirect, request, jsonify,url_for
from functools import wraps
import os
from pymongo import MongoClient
from flask_cors import CORS
import logging
from flask import Flask, request, jsonify
# from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


app = Flask(__name__)
CORS(app, resources={r"/load_acc_by_user": {"origins": ["http://52.41.36.82", "http://54.191.253.12", "http://44.226.122.3"]}})

app.secret_key = "your_secret_key"  # Add a secret key for session management

# Connect to MongoDB
client = MongoClient("mongodb+srv://Samarth_7:Sam_mongo_atlas@iitdhcluster.a1gizlj.mongodb.net/?retryWrites=true&w=majority&appName=iitdhcluster")
# client = MongoClient("mongodb://localhost:27017")



db = client.admi 
users_collection = db.user_login  

allb = client.all_books 
b = allb.books2  

announce = client.admi
announcements = announce.announcements

issue = client.admi
acc = client.admi

ofs = client.admi
stock = ofs.out_of_stock


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

@app.route('/loadallissueeqs', methods=['GET'])
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

    req = data['req']
    
    email = req['email']
    subject = f'Book Issued: {req["bookname"]}'
    message = f'Hello {req["Name"]},\n\nYour book "{req["bookname"]}" has been successfully issued.\nThe book has been issued for 15 days, please return it before deadline.\n\nBest regards,\nLibrary Team'


    sender_email = '220010052@iitdh.ac.in'
    sender_password = 'vqst edwo frvk ygoe'

    sender_email = 'pssquare169@gmail.com'
    sender_password = 'ChitnisKumarJha'

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())

        return jsonify({'success': True}), 200

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 500
    
    # return jsonify({"message": "issue req added", "id": str(acc_request_id)}), 201

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


@app.route('/add_new_book' ,methods=['POST'])
def add_new_book():
    data = request.get_json()
    new_book = {
        "title" : data['bt'],
        "description" : data['bdesc'],
        "author" : data['ba'],
        "genre" : data['bg'],
        "department" : data['bdept'],
        "count" : data['bc'],
        "publisher" : data['bp']
    }
    new_book_id = b.insert_one(new_book).inserted_id
    return jsonify({"message": "issue req added", "id": str(new_book_id)}), 201


@app.route('/out_of_stock', methods=['POST'])
def out_of_stick():
    data = request.get_json()
    print(data)

    fields = {
        "title": data['title'],
        "author": data['author'],
        "publisher": data['publisher']
    }

    is_duplicate = stock.find_one(fields)

    if not is_duplicate:
    
        ofs_book = {
            "title" : data['title'],
            "description" : data['description'],
            "author" : data['author'],
            "genre" : data['genre'],
            "department" : data['department'],
            "count" : data['count'],
            "publisher" : data['publisher']
        }
        out_of_stock_book_id = stock.insert_one(ofs_book).inserted_id
        return jsonify({"message": "req added", "id": str(out_of_stock_book_id)}), 201

    else:
        return jsonify({"message": "Book already exists", "id": str(is_duplicate['_id'])}), 201
        

@app.route('/load_out_of_stock_books' , methods=['GET'])
def load_out_of_stock_books():
    ofs_books = stock.find().sort("timestamp", +1)
    return dumps(ofs_books), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
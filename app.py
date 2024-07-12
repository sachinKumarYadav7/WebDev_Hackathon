from flask import Flask, render_template, session, redirect, request, jsonify,url_for
from functools import wraps
import os
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
import logging
from flask import Flask, request, jsonify
# from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from Recommender_System.recommender import most_issued_books

import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

app = Flask(__name__)
CORS(app)

app.secret_key = "your_secret_key"  # Add a secret key for session management

# Connect to MongoDB
client = MongoClient("mongodb+srv://Samarth_7:Sam_mongo_atlas@iitdhcluster.a1gizlj.mongodb.net/?retryWrites=true&w=majority&appName=iitdhcluster")
# client = MongoClient("mongodb://localhost:27017")

# ===================================================================================================================================================================

# Accessing the book from database
books_collection = client['all_books']['books2']
user_interactions_collection = client['all_books']['user_rating']

# Load your data here
books = pd.DataFrame(list(books_collection.find()))
books['book_id'] = range(1, len(books) + 1)
books['book_id'] = books['book_id'].apply(lambda x: str(x).zfill(6)).astype(int)
user_interactions = pd.DataFrame(list(user_interactions_collection.find()))

# Ensure all entries in combined_features are strings
books['combined_features'] = (books['title'].fillna('') + ' ' + 
                              books['description'].fillna('') + ' ' + 
                              books['author'].fillna('') + ' ' + 
                              books['genre'].fillna('') + ' ' + 
                              books['department'].fillna(''))

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(books['combined_features'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

print(user_interactions.head())
print(user_interactions.columns)


# Collaborative Filtering Setup
user_book_ratings = user_interactions.pivot(index='user_id', columns='book_id', values='rating').fillna(0) + user_interactions.pivot(index='user_id', columns='book_id', values='borrow_count').fillna(0)
R = user_book_ratings.values
user_ratings_mean = np.mean(R, axis=1)
R_demeaned = R - user_ratings_mean.reshape(-1, 1)

# Determine the appropriate value of k based on the shape of R_demeaned
num_users, num_books = R_demeaned.shape
k = min(num_users, num_books) - 1  # Set k to be less than the smaller dimension

# Perform matrix factorization with the adjusted value of k
U, sigma, Vt = svds(R_demeaned, k=k)
sigma = np.diag(sigma)
predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
predicted_ratings_books = pd.DataFrame(predicted_ratings, columns=user_book_ratings.columns)

# Define recommendation functions
def get_content_based_recommendations(title, cosine_sim=cosine_sim, num_recommendations=2):
    try:
        idx = books[books['title'] == title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:num_recommendations]
        book_indices = [i[0] for i in sim_scores]
        return books.iloc[book_indices][['title', 'author', 'genre']]
    except IndexError:
        logging.error(f"Title '{title}' not found in books dataset")
        return pd.DataFrame(columns=['title', 'author', 'genre'])

def get_collaborative_filtering_recommendations(user_id, num_recommendations=2):
    try:
        user_idx = user_id - 1
        user_ratings = predicted_ratings_books.iloc[user_idx]
        sorted_indices = np.argsort(user_ratings)[::-1]
        recommended_indices = sorted_indices[:num_recommendations]
        return books[books['book_id'].isin(predicted_ratings_books.columns[recommended_indices])][['title', 'author', 'genre']]
    except IndexError:
        logging.error(f"User ID '{user_id}' not found in user interactions dataset")
        return pd.DataFrame(columns=['title', 'author', 'genre'])

def get_hybrid_recommendations(title, user_id, cosine_sim, num_recommendations=3):
    content_based_recs = get_content_based_recommendations(title, cosine_sim)
    collaborative_recs = get_collaborative_filtering_recommendations(user_id, num_recommendations)
    combined_recs = pd.concat([content_based_recs, collaborative_recs]).drop_duplicates().head(num_recommendations)
    return combined_recs

@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        title = request.args.get('title')
        # print("\n\n", title,"\n\n")
        user_id = int(request.args.get('user_id'))
        # print("\n\n", user_id,"\n\n")
        num_recommendations = int(request.args.get('num_recommendations', 2))
        
        logging.debug(f"Received recommendation request for title: {title}, user_id: {user_id}, num_recommendations: {num_recommendations}")
        
        # Validate parameters
        if title not in books['title'].values:
            logging.error(f"Title '{title}' not found in books dataset")
            return jsonify({"error": "Title not found"}), 404

        if user_id not in user_interactions['user_id'].values:
            logging.error(f"User ID '{user_id}' not found in user interactions dataset")
            return jsonify({"error": "User ID not found"}), 404

        recommendations = get_hybrid_recommendations(title, user_id, cosine_sim, num_recommendations)
        
        logging.debug(f"Generated recommendations: {recommendations}")
        
        return recommendations.to_json(orient='records')
    except Exception as e:
        logging.error(f"Error in recommendation process: {e}")
        return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500
    
@app.route('/recommend1', methods=['GET'])
def recommend1():
    try:
        title = request.args.get('title')
        num_recommendations = int(request.args.get('num_recommendations', 2))
        
        if title not in books['title'].values:
            return jsonify({"error": "Title not found"}), 404

        recommendations = get_content_based_recommendations(title, cosine_sim, num_recommendations)
        return recommendations.to_json(orient='records')
    except Exception as e:
        return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500



# ====================================================================================================================================================================



# ==========================================Most Issued book BranchWise==========================================================================================================================
data = client['admi']['accepted']

# Fetch all records from the 'accepted' collection
records = list(data.find())

# Create a DataFrame from the MongoDB records
df = pd.DataFrame(records)

# Function to extract fields from 'req' dictionary
def extract_req_field(req, field):
    return req.get(field, None)

# Extract 'email' and 'bookname' into separate columns
df['email'] = df['req'].apply(lambda x: extract_req_field(x, 'email'))
df['bookname'] = df['req'].apply(lambda x: extract_req_field(x, 'bookname'))

# Function to extract branch year from email
def extract_branch_year(email):
    return str(email.split('@')[0])[:-3]

# Add a column for BranchYear
df['BranchYear'] = df['email'].apply(extract_branch_year)

# Group by BookName and BranchYear to get the count of issues
issue_counts = df.groupby(['bookname', 'BranchYear']).size().reset_index(name='IssueCount')

def most_issued_books(dataset, branch_year):
    filtered_data = dataset[dataset['BranchYear'] == branch_year]
    sorted_data = filtered_data.sort_values(by='IssueCount', ascending=False)
    top_books = sorted_data.head(2)['bookname'].tolist()
    return top_books

@app.route('/recommend2', methods=['GET'])
def recommend2():
    try:
        user_email = session['user']['email']
        branch_year = extract_branch_year(user_email)
        recommendations = most_issued_books(issue_counts, branch_year)
        
        logging.debug(f"Generated recommendations: {recommendations}")
        
        return jsonify(recommendations)
    except Exception as e:
        logging.error(f"Error in recommendation process: {e}")
        return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500

# ====================================================================================================================================================================





# =========================================Search_History========================================================================================================
database = client['search_history_db']
@app.route('/search2', methods=['POST'])
def search2():
    if 'user' not in session:
        return jsonify({'message': 'User not logged in'}), 403

    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'message': 'Search query cannot be empty'}), 400

    user_id = session['user']['email'][:-12:]

    # Save search history to the database
    new_search = {
        'user_id': user_id,
        'search_query': query,
        'timestamp': datetime.utcnow()
    }
    database.search_history.insert_one(new_search)
    app.logger.info('Search query recorded for user_id: %s', user_id)

    # Perform the search
    results = list(b.find({"title": {"$regex": query, "$options": "i"}}))

    for book in results:
        book['_id'] = str(book['_id'])

    return jsonify(results)



@app.route('/search-history', methods=['GET'])
def get_search_history():
    if 'user' not in session:
        return jsonify({'message': 'User not logged in'}), 403

    user_id = session['user']['_id']
    history = database.search_history.find({'user_id': user_id})

    history_data = [{'search_query': record['search_query'], 'timestamp': record['timestamp']} for record in history]

    return jsonify(history_data), 200


# ===============================================================================================================================================================


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
    limit = int(request.args.get('limit', 140))
    skip = (page - 1) * limit
    
    books = list(b.find().skip(skip).limit(limit))
    for book in books:
        book['_id'] = str(book['_id'])  
    
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
        "genre" : data['genre'],
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
    

@app.route('/book_returned/<id>', methods=['POST'])
def book_returned(id):
    try:
        db.accepted.delete_one({'_id':ObjectId(id) })
        return jsonify({'status': 'success', 'message': 'Entry deleted successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/delete_announcement/<id>', methods=['POST'])
def delete_announcement(id):
    try:
        db.announcements.delete_one({'_id':ObjectId(id) })
        return jsonify({'status': 'success', 'message': 'Entry deleted successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
@app.route('/deletebook/<book_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
def delete_book(book_id):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return '', 200, headers
    
    try:
        allb.books2.delete_one({'_id': ObjectId(book_id)})
        return jsonify({'status': 'success', 'message': 'Book deleted successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
@app.route('/update_book/<book_id>', methods=['POST'])
def update_book(book_id):
    try:
        data = request.get_json()

        update_fields = {
            'title': data['bt'],
            'author': data['ba'],
            'description': data['bdesc'],
            'genre': data['bg'],
            'department': data['bdept'],
            'count': data['bc'],
            'publisher': data['bp']
        }
        
        result = allb.books2.update_one(
            {'_id': ObjectId(book_id)},
            {'$set': update_fields}
        )
        
        if result.matched_count == 0:
            return jsonify({'status': 'error', 'message': 'Book not found'}), 404

        return jsonify({'status': 'success', 'message': 'Book updated successfully'}), 200
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
    sender_password = 'miukevztzdguwgkz'
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
    try:
        book_count = int(data['bc'])
    except ValueError:
        return jsonify({"error": "Invalid count value, must be an integer"}), 400
    
    new_book = {
        "title": data['bt'],
        "description": data['bdesc'],
        "author": data['ba'],
        "genre": data['bg'],
        "department": data['bdept'],
        "count": book_count,  # Ensure this is an int
        "publisher": data['bp']
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


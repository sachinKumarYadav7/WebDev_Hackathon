from flask import Flask, jsonify,render_template, session
from app import app
from user.models import User
from bson import ObjectId  # Import ObjectId from bson module



@app.route('/user/login', methods=['POST'])
def login():
    user = User().login()  
    if 'error' in user:
        return jsonify({"error": user['error']}), 401  # Return error response if login fails

    # Convert ObjectId to string for serialization
    user['_id'] = str(user['_id'])

    return jsonify(user), 200  # Return user data as JSON response


@app.route('/search')
def search():
    return render_template('search.html')


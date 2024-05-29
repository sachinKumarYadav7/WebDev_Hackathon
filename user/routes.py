from flask import Flask, jsonify
from app import app
from user.models import User
from bson import ObjectId  # Import ObjectId from bson module

@app.route('/user/signup', methods=['POST'])
def signup():
  return User().signup()

@app.route('/user/signout')
def signout():
  return User().signout()



@app.route('/user/login', methods=['POST'])
def login():
    user = User().login()  # Assuming User().login() returns the user's data
    if 'error' in user:
        return jsonify({"error": user['error']}), 401  # Return error response if login fails

    # Convert ObjectId to string for serialization
    user['_id'] = str(user['_id'])

    return jsonify(user), 200  # Return user data as JSON response

@app.route('/logout')
def logout():
    return User().logout()


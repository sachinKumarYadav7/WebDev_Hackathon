from flask import session, redirect, url_for, jsonify, request,render_template
from bson import ObjectId

class User:
    def __init__(self, db):
        self.db = db

    def start_session(self, user):
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        user.pop('password', None)
        session['user'] = user
        session['logged_in'] = True
        return redirect(url_for('home'))

    def login(self):
        user = self.db.user_login.find_one({
            "email": request.form.get('email')
        })

        if user and request.form.get('password') == user['password']:
            return self.start_session(user)

        error_message = "Invalid login credentials. Please try again."
        return render_template('login.html', error=error_message)

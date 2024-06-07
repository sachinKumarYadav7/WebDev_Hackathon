from flask import session, redirect, url_for, jsonify, request, render_template
from bson import ObjectId

class User:
    def __init__(self, db):
        self.db = db

    def start_session(self, user, is_admin=False):
        user['_id'] = str(user['_id'])  
        user.pop('password', None)
        session['user'] = user
        session['logged_in'] = True
        session['is_admin'] = is_admin

        if is_admin:
            return redirect(url_for('admin_home'))
        else:
            return redirect(url_for('home'))

    def login(self):
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = self.db.user_login.find_one({"email": email})
        
        if user and password == user['password']:
            return self.start_session(user, is_admin=False)
        
        admin = self.db.admin_login.find_one({"email": email})
        
        if admin and password == admin['password']:
            return self.start_session(admin, is_admin=True)

        error_message = "Invalid login credentials. Please try again."
        return render_template('login.html', error=error_message)

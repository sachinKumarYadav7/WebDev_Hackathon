import bcrypt
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.your_database  # Replace 'your_database' with your actual database name
users_collection = db.users  # Replace 'users' with your actual collection name

def verify_login(email, password):
    # Query MongoDB to find user by email
    user = users_collection.find_one({'email': email})

    if user:
        # Extract hashed password from the user document
        hashed_password = user.get('password')

        # Verify the user's input password against the hashed password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return True  # Password matches
        else:
            return False  # Password does not match
    else:
        return False  # User with the provided email not found

# Example usage:
email = "220010052@iitdh.ac.in"
password = "user_input_password"

if verify_login(email, password):
    print("Login successful")
else:
    print("Login failed")

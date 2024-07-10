from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialize extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# User Registration
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if username and email and password:
        # Check if the username already exists
        if mongo.db.users.find_one({'username': username}):
            return jsonify({'message': 'Username already exists!'}), 400

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user data into MongoDB
        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })

        return jsonify({'message': 'Registration successful!'}), 201
    else:
        return jsonify({'message': 'Please provide all required fields!'}), 400

# User Login
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    user = mongo.db.users.find_one({'username': username})

    if user and bcrypt.check_password_hash(user['password'], password):
        # Create JWT Token
        access_token = create_access_token(identity=username)
        return jsonify({'token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password!'}), 401

# Protected Route Example
@app.route('/auth/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Hello, {current_user}!'})

if __name__ == '__main__':
    app.run(debug=True)

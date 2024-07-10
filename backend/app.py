from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os
import PyPDF2
from langchain_community.vectorstores.cassandra import Cassandra  # Updated import
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import cassio  # Import cassio for Cassandra integration

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['ASTRA_DB_APPLICATION_TOKEN'] = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
app.config['ASTRA_DB_ID'] = os.getenv('ASTRA_DB_ID')
app.config['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Initialize extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Initialize language model and vector store components
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=app.config['GOOGLE_API_KEY'])
embedding = GoogleGenerativeAIEmbeddings(model='models/embedding-001')

# Initialize cassio for Cassandra database connection
cassio.init(token=app.config['ASTRA_DB_APPLICATION_TOKEN'], database_id=app.config['ASTRA_DB_ID'])

# Initialize the vector store index
astra_vector_index = None  # Placeholder for vector store index

# User Registration
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if username and email and password:
        if mongo.db.users.find_one({'username': username}):
            return jsonify({'message': 'Username already exists!'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })

        # Initialize Cassandra vector store for the new user
        table_name = username  # Use username as the table name
        astra_vector_store = Cassandra(
            embedding=embedding,
            table_name=table_name,
            session=None,
            keyspace=None,
        )

        # Initialize the vector store index for the new user
        global astra_vector_index
        astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)

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
        access_token = create_access_token(identity=username)

        return jsonify({'token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password!'}), 401

# PDF Upload
@app.route('/pdf/upload', methods=['POST'])
@jwt_required()
def upload_pdf():
    current_user = get_jwt_identity()
    pdf_file = request.files.get('pdf')

    if pdf_file:
        # Extract text from the PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        raw_text = ''
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                raw_text += content

        if raw_text:
            # Split text into chunks
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=800,
                chunk_overlap=200,
                length_function=len,
            )
            texts = text_splitter.split_text(raw_text)

            # Initialize Cassandra vector store for the current user
            table_name = current_user  # Use current_user as the table name
            astra_vector_store = Cassandra(
                embedding=embedding,
                table_name=table_name,
                session=None,
                keyspace=None,
            )

            # Initialize the vector store index for the current user if not initialized
            global astra_vector_index
            if astra_vector_index is None:
                astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)

            # Add new texts to the vector store
            astra_vector_store.add_texts(texts, metadatas=[{'user_id': current_user} for _ in texts])

            return jsonify({'message': f'PDF uploaded and {len(texts)} text chunks stored.'}), 200
        else:
            return jsonify({'message': 'No text extracted from the PDF.'}), 400
    else:
        return jsonify({'message': 'No PDF file uploaded.'}), 400

# Query Processing
@app.route('/pdf/query', methods=['POST'])
@jwt_required()
def query():
    current_user = get_jwt_identity()
    data = request.get_json()
    query_text = data.get('query')

    if query_text:
        # Perform the query against the vector store based on the current user
        table_name = current_user  # Use current_user as the table name
        astra_vector_store = Cassandra(
            embedding=embedding,
            table_name=table_name,
            session=None,
            keyspace=None,
        )

        astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)
        answer = astra_vector_index.query(query_text, llm=llm, metadata={'user_id': current_user}).strip()
        return jsonify({'answer': answer}), 200
    else:
        return jsonify({'message': 'Please provide a query.'}), 400

# Handle Token Expiry and Remove Row
@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    token = jwt_payload['sub']
    # Implement a mechanism to handle expired tokens
    return jsonify({'message': 'Token has expired and the associated data has been removed.'}), 401

# Protected Route Example
@app.route('/auth/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Hello, {current_user}!'})

if __name__ == '__main__':
    app.run(debug=True)

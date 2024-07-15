# PDF Query Bot

**PDF Query Bot** is an advanced web-based application that allows users to interact with PDF documents using natural language queries. It employs **Google Gemini LLM** for intelligent query responses and **Astradb** for efficient storage and management of PDF document vectors.

## Live Preview

You can interact with the [PDFQueryBot Frontend](https://your-streamlit-live-preview-url) to see the application in action.


## Overview

PDFQueryBot provides a platform where users can upload PDF files, ask questions about their content, and get accurate answers using natural language processing. The backend is built with Flask, integrating with Google Gemini LLM for language models and Astradb for storing and managing PDF content vectors.

## Features

- **PDF Upload**: Upload PDF files to be processed.
- **Query Processing**: Submit text-based queries to extract information from the PDF.
- **Google Gemini LLM Integration**: Leverages advanced language models for interpreting and responding to queries.
- **Astradb for Vector Storage**: Uses Astradb for efficient storage of PDF content vectors and query results.
- **User Authentication**: Secure registration and login functionality.



## Technologies Used

- **[Google Gemini LLM](https://www.google.com/ai/gemini/)**: For natural language understanding and generating responses.
- **[Astradb](https://www.astra.datastax.com/)**: NoSQL database service for **storing PDF content vectors** and managing query results.
- **[MongoDB](https://www.mongodb.com/)**: NoSQL database for **user data management**.
- **[Flask](https://flask.palletsprojects.com/en/2.3.x/)**: Web framework for building the application.
- **[Gunicorn](https://gunicorn.org/)**: WSGI HTTP Server for running the Flask app in production.
- **[Docker](https://www.docker.com/)**: Containerization platform for deploying the application.

## Getting Started

To get started with **PDF Query Bot**, you need to set up the backend and connect it with the frontend, or use the provided API endpoints for query processing.
### Prerequisites

- **Docker**: Ensure Docker is installed on your machine.

### Clone the Repository

```bash
[git clone https://github.com/yourusername/PDFQueryBot.git](https://github.com/Prabhanshu76/PDF-Query-Bot.git)
cd PDF-Query-Bot
### Set Up Environment Variables
```

Create a `.env` file in the root directory with the following content:

```plaintext
SECRET_KEY=your_secret_key
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.nvnkbds.mongodb.net/<db_name>?retryWrites=true&w=majority
JWT_SECRET_KEY=your_jwt_secret_key
ASTRA_DB_APPLICATION_TOKEN=your_astra_db_application_token
ASTRA_DB_ID=your_astra_db_id
GOOGLE_API_KEY=your_google_api_key
```
## Running the Backend Locally

To run the **PDFQueryBot** backend locally, follow these steps:

### 1. Build the Docker Image

Build the Docker image using the following command:

```bash
docker build -t pdfquerybot-backend .
```
### 2. Run the Docker Container

Run the Docker container with the following command:

```bash
docker run -p 5000:5000 --env-file .env pdfquerybot-backend
```

### 3. Access the APIs

Once the container is running, you can access the backend APIs at the following endpoints:

- **Registration**: `POST http://localhost:5000/auth/register`  
  Register a new user. **No authentication required.**

- **Login**: `POST http://localhost:5000/auth/login`  
  Log in an existing user and obtain a JWT token. **No authentication required.**

- **Upload PDF**: `POST http://localhost:5000/pdf/upload`  
  Upload a PDF file and store the extracted text as vectors. **Requires authentication** (JWT token in the Authorization header).

- **Query Processing**: `POST http://localhost:5000/pdf/query`  
  Submit a query against the uploaded PDF content and receive a response. **Requires authentication** (JWT token in the Authorization header).

- **Sanity Check**: `GET http://localhost:5000/`  
  A simple endpoint to check if the application is up and running. **No authentication required.**

## Sample API Calls and Responses

Below are some example API calls along with the expected responses for each endpoint.

### 1. User Registration

**Endpoint:** `POST http://localhost:5000/auth/register`

**Request:**

```bash
curl -X POST "http://localhost:5000/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "username": "exampleUser",
  "email": "example@example.com",
  "password": "examplePassword"
}'
```
#### API Response

##### Success Response

**HTTP Status Code:** 200 OK

**Response:**
```json
{
  "message": "Registration successful!"
}
```

### 2. User Login

**Endpoint:** `POST http://localhost:5000/auth/login`

**Request:**

```bash
curl -X POST "http://localhost:5000/auth/login" \
-H "Content-Type: application/json" \
-d '{
  "username": "exampleUser",
  "password": "examplePassword"
}'

```
#### API Response

##### Success Response

**HTTP Status Code:** 200 OK

**Response:**
```json
{
  "token": "your-jwt-token"
}
```

### 3. Upload PDF

**Endpoint:** `POST http://localhost:5000/pdf/upload`

**Request:**

```bash
curl -X POST "http://localhost:5000/pdf/upload" \
-H "Authorization: Bearer your-jwt-token" \
-F "pdf=@path/to/your/pdf-file.pdf"

```
#### API Response 

##### Success Response

**HTTP Status Code:** 200 OK

**Response:**
```json
{
  "message": "PDF uploaded and 10 text chunks stored."
}
```


### 4. Query Processing

**Endpoint:** `POST http://localhost:5000/auth/register`

**Request:**

```bash
curl -X POST "http://localhost:5000/pdf/query" \
-H "Authorization: Bearer your-jwt-token" \
-H "Content-Type: application/json" \
-d '{
  "query": "What is the main topic of the document?"
}'

```
#### API Response 

##### Success Response

**HTTP Status Code:** 200 OK

**Response:**
```json
{
  "answer": "The main topic of the document is about advanced data analytics techniques."
}
```

### 5. Sanity Check

**Endpoint:** `POST http://localhost:5000/`

#### API Response 

##### Success Response

**HTTP Status Code:** 200 OK

**Response:**
```json
{
  "message": "API is up and running!"
}
```

## References

- **[Google Gemini LLM](https://www.google.com/ai/gemini/)**: The AI model used for natural language understanding and generating responses.





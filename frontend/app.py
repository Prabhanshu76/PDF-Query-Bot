import streamlit as st
import requests
from datetime import datetime
import time
import re

# API endpoints
REGISTER_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/register"
LOGIN_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/login"
LOGOUT_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/logout"
UPLOAD_PDF_URL = "https://prabhanshu76-spectre-bot.hf.space/pdf/upload"
QUERY_PDF_URL = "https://prabhanshu76-spectre-bot.hf.space/pdf/query"
PROTECTED_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/protected"

def init_session_state():
    """Initialize session state variables"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "token" not in st.session_state:
        st.session_state.token = None
    if "pdf_uploaded" not in st.session_state:
        st.session_state.pdf_uploaded = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_pdf" not in st.session_state:
        st.session_state.current_pdf = None

def handle_api_request(request_func, url, error_message="API request failed", **kwargs):
    """Generic API request handler with error handling"""
    try:
        response = request_func(url, **kwargs)
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"{error_message}: {str(e)}")
        return None

def register(username, email, password):
    return handle_api_request(
        requests.post,
        REGISTER_URL,
        error_message="Registration failed",
        json={"username": username, "email": email, "password": password}
    )

def login(username, password):
    response = handle_api_request(
        requests.post,
        LOGIN_URL,
        error_message="Login failed",
        json={"username": username, "password": password}
    )
    return response.json().get('token') if response and response.status_code == 200 else None

def logout():
    """Handle user logout with API call"""
    if st.session_state.token:
        try:
            headers = {'Authorization': f'Bearer {st.session_state.token}'}
            response = requests.post(LOGOUT_URL, headers=headers)
            
            if response.status_code == 200:
                # First set logged_in to False
                st.session_state.logged_in = False
                # Then clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                return True
            return False
        except requests.exceptions.RequestException:
            return False
    return False

def upload_pdf(file, token):
    headers = {'Authorization': f'Bearer {token}'}
    files = {'pdf': (file.name, file, 'application/pdf')}
    return handle_api_request(
        requests.post,
        UPLOAD_PDF_URL,
        error_message="PDF upload failed",
        files=files,
        headers=headers
    )

def query_pdf(query, token):
    headers = {'Authorization': f'Bearer {token}'}
    return handle_api_request(
        requests.post,
        QUERY_PDF_URL,
        error_message="Query failed",
        json={"query": query},
        headers=headers
    )

def show_login_signup_screen():
    tabs = st.tabs(["Login", "Signup"])
    
    with tabs[0]:
        st.subheader("Login")
        with st.form("login_form"):
            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login")
            
            if login_submitted:
                if login_username and login_password:
                    token = login(login_username, login_password)
                    if token:
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.session_state.token = token
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.error("Please provide both username and password.")

    with tabs[1]:
        st.subheader("Signup")
        with st.form("signup_form"):
            signup_username = st.text_input("Username")
            signup_email = st.text_input("Email")
            signup_password = st.text_input("Password", type="password")
            signup_confirm_password = st.text_input("Confirm Password", type="password")
            signup_submitted = st.form_submit_button("Sign Up")
            
            if signup_submitted:
                if not all([signup_username, signup_email, signup_password, signup_confirm_password]):
                    st.error("Please fill in all fields.")
                elif signup_password != signup_confirm_password:
                    st.error("Passwords do not match.")
                elif not is_valid_email(signup_email):
                    st.error("Invalid email format.")
                else:
                    response = register(signup_username, signup_email, signup_password)
                    if response and response.status_code == 201:
                        st.success("Signed up successfully! Please login.")
                    elif response and response.status_code == 400:
                        st.error("Username already exists!")
                    else:
                        st.error("Error during registration.")

def display_message(role, content, timestamp=None):
    if role == "user":
        message_alignment = "flex-end"
        background_color = "#007bff"
        text_color = "white"
    else:
        message_alignment = "flex-start"
        background_color = "#f0f0f0"
        text_color = "black"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: {message_alignment}; margin-bottom: 10px;">
            <div style="background-color: {background_color}; color: {text_color}; padding: 10px; 
                      border-radius: 15px; max-width: 70%; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                {content}
                {f'<div style="font-size: 0.8em; opacity: 0.7; margin-top: 5px;">{timestamp}</div>' if timestamp else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_main_screen():
    # Sidebar for PDF upload and logout
    with st.sidebar:
        st.title("PDF Management")
        
        # Updated logout button with API call
        if st.button("Logout"):
            if logout():
                st.success("Logged out successfully!")
                time.sleep(1)  # Give user time to see the success message
                st.rerun()
            else:
                st.error("Logout failed. Please try again.")
        
        # PDF upload section
        st.header("Upload PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None and (not st.session_state.current_pdf or st.session_state.current_pdf != uploaded_file.name):
            response = upload_pdf(uploaded_file, st.session_state.token)
            if response and response.status_code == 200:
                st.session_state.pdf_uploaded = True
                st.session_state.current_pdf = uploaded_file.name
                st.session_state.messages = []  # Clear messages for new PDF
                st.success("PDF uploaded successfully!")
                st.rerun()
            else:
                st.error("Failed to upload PDF.")

    # Main chat interface
    st.title("Chat with your PDF")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            display_message(
                message["role"],
                message["content"],
                message.get("timestamp")
            )

    # Query input
    if st.session_state.pdf_uploaded:
        with st.form(key="query_form", clear_on_submit=True):
            query = st.text_input("Ask a question about your PDF:", key="query_input")
            submit_button = st.form_submit_button("Send")
            
            if submit_button and query:
                # Add user message
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    "role": "user",
                    "content": query,
                    "timestamp": timestamp
                })
                
                # Get bot response
                response = query_pdf(query, st.session_state.token)
                if response and response.status_code == 200:
                    answer = response.json().get('answer', 'No answer received from the server.')
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "timestamp": timestamp
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I apologize, but I couldn't process your question. Please try again.",
                        "timestamp": timestamp
                    })
                st.rerun()
    else:
        st.info("Please upload a PDF to start chatting.")

def is_valid_email(email):
    email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, email)


def main():
    st.set_page_config(
        page_title="PDF Query Chatbot",
        page_icon="📚",
        initial_sidebar_state="expanded"
    )

    st.title("PDF Query Chatbot")
  
    init_session_state()
    
    if not st.session_state.logged_in:
         show_login_signup_screen()
    else:
         show_main_screen()


if __name__ == "__main__":
    main()

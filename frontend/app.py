import streamlit as st
import requests
import re  # Import re for regular expressions

# API Endpoints
REGISTER_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/register"
LOGIN_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/login"

# Function to validate email format
def is_valid_email(email):
    email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, email)

# Function to handle user registration
def register(username, email, password):
    response = requests.post(REGISTER_URL, json={
        "username": username,
        "email": email,
        "password": password
    })
    return response

# Function to handle user login
def login(username, password):
    response = requests.post(LOGIN_URL, json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        # Extract token from response
        token = response.json().get('token')
        return token
    else:
        return None

def main():
    st.title("PDF Query Chatbot")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        show_main_screen()
    else:
        show_login_signup_screen()

def show_login_signup_screen():
    tabs = st.tabs(["Login", "Signup"])

    with tabs[0]:
        st.subheader("Login")

        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if login_username and login_password:
                token = login(login_username, login_password)
                if token:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.token = token  # Save the access token
                    st.success("Logged in successfully!")
                    st.experimental_rerun()  # Rerun the app to update the UI immediately
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Please provide both username and password.")

    with tabs[1]:
        st.subheader("Signup")

        signup_username = st.text_input("Username", key="signup_username")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

        if st.button("Signup"):
            if not signup_username or not signup_email or not signup_password or not signup_confirm_password:
                st.error("Please fill in all fields.")
            elif signup_password != signup_confirm_password:
                st.error("Passwords do not match.")
            elif not is_valid_email(signup_email):
                st.error("Invalid email format.")
            else:
                response = register(signup_username, signup_email, signup_password)
                if response.status_code == 201:
                    st.success("Signed up successfully!")
                elif response.status_code == 400:
                    st.error("Username already exists!")
                else:
                    st.error("Error during registration.")

def show_main_screen():
    # Create a top-level layout with two columns
    col1, col2 = st.columns([9, 2])  # 9 parts for the content, 2 parts for the button
    
    with col1:
        st.subheader("Upload PDF and Query")
    
    with col2:
        if st.button("Logout"):
            logout()

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        st.session_state.pdf_file = uploaded_file

    if "pdf_file" in st.session_state:
        st.write("PDF uploaded successfully!")

        query = st.text_input("Enter your query")

        if st.button("Submit Query"):
            if query:
                response = process_query(query)  # Placeholder for query processing function
                st.write("Current Query: ", query)
                st.write("Reply: ", response)
            else:
                st.error("Please enter a query.")

def process_query(query):
    # Placeholder function for query processing
    # Replace this with actual logic to process the query and return a response
    # You will need to send the query to an appropriate API endpoint
    return f"Response to '{query}'"

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None  # Clear the username
    st.session_state.token = None  # Clear the token
    st.experimental_rerun()  # Rerun the app to update the UI immediately

if __name__ == "__main__":
    main()

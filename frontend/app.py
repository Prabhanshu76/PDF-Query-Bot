import streamlit as st
import requests

REGISTER_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/register"
LOGIN_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/login"
UPLOAD_PDF_URL = "https://prabhanshu76-spectre-bot.hf.space/pdf/upload"
QUERY_PDF_URL = "https://prabhanshu76-spectre-bot.hf.space/pdf/query"
PROTECTED_URL = "https://prabhanshu76-spectre-bot.hf.space/auth/protected"

def is_valid_email(email):
    import re
    email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, email)

def register(username, email, password):
    response = requests.post(REGISTER_URL, json={
        "username": username,
        "email": email,
        "password": password
    })
    return response

def login(username, password):
    response = requests.post(LOGIN_URL, json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        token = response.json().get('token')
        return token
    else:
        return None

def call_protected(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(PROTECTED_URL, headers=headers)
    return response

def upload_pdf(file, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    files = {'pdf': (file.name, file, 'application/pdf')}
    response = requests.post(UPLOAD_PDF_URL, files=files, headers=headers)
    return response

def query_pdf(query, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(QUERY_PDF_URL, json={"query": query}, headers=headers)
    return response

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
                    st.session_state.token = token
                    st.success("Logged in successfully!")

                    protected_response = call_protected(token)
                    st.write(f"Protected Route Status Code: {protected_response.status_code}")
                    st.write(f"Protected Route Response: {protected_response.json()}")

                    st.experimental_rerun()
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
    col1, col2 = st.columns([9, 2])

    with col1:
        st.subheader("Upload PDF and Query")
    
    with col2:
        if st.button("Logout"):
            logout()

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        response = upload_pdf(uploaded_file, st.session_state.token)
        st.write(f"Response Status Code: {response.status_code}")
        st.write(f"Response Text: {response.text}")
        if response.status_code == 200:
            st.success("PDF uploaded successfully!")
            st.session_state.pdf_uploaded = True
        else:
            st.error("Failed to upload PDF.")

    if "pdf_uploaded" in st.session_state and st.session_state.pdf_uploaded:
        query = st.text_input("Enter your query")

        if st.button("Submit Query"):
            if query:
                response = query_pdf(query, st.session_state.token)
                if response.status_code == 200:
                    answer = response.json().get('answer', 'No answer received from the server.')
                    st.write("Current Query: ", query)
                    st.write("Answer: ", answer)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            else:
                st.error("Please enter a query.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.token = None
    st.session_state.pdf_uploaded = False
    st.experimental_rerun()

if __name__ == "__main__":
    main()

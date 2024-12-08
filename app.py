import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from tools.fetch_stock_info import Analyze_stock

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, 
                  password TEXT,
                  email TEXT,
                  full_name TEXT,
                  created_at DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS queries
                 (username TEXT, query TEXT, response TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_credentials(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username=?', (username,))
    stored_password = c.fetchone()
    conn.close()
    if stored_password:
        return stored_password[0] == make_hash(password)
    return False

def username_exists(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

def email_exists(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT email FROM users WHERE email=?', (email,))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_query(username, query, response):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO queries VALUES (?, ?, ?, ?)', 
              (username, query, response, datetime.now()))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT query, response, timestamp FROM queries WHERE username=? ORDER BY timestamp DESC', 
              (username,))
    history = c.fetchall()
    conn.close()
    return history

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize database
init_db()

# Sidebar for authentication
with st.sidebar:
    if not st.session_state.logged_in:
        st.header("Login/Register")
        action = st.radio("Choose action:", ["Login", "Register"])
        
        if action == "Register":
            st.subheader("Create New Account")
            with st.form("registration_form"):
                new_username = st.text_input("Username*")
                new_email = st.text_input("Email*")
                new_full_name = st.text_input("Full Name*")
                new_password = st.text_input("Password*", type="password")
                confirm_password = st.text_input("Confirm Password*", type="password")
                
                submit_button = st.form_submit_button("Register")
                
                if submit_button:
                    if not all([new_username, new_email, new_full_name, new_password, confirm_password]):
                        st.error("All fields are required!")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long!")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match!")
                    elif username_exists(new_username):
                        st.error("Username already exists!")
                    elif email_exists(new_email):
                        st.error("Email already registered!")
                    elif not '@' in new_email:
                        st.error("Please enter a valid email address!")
                    else:
                        conn = sqlite3.connect('users.db')
                        c = conn.cursor()
                        c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', 
                                (new_username, make_hash(new_password), 
                                 new_email, new_full_name, datetime.now()))
                        conn.commit()
                        conn.close()
                        st.success("Registration successful! Please login.")
                
        else:  # Login
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_button = st.form_submit_button("Login")
                
                if login_button:
                    if check_credentials(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
    else:
        st.write(f"Logged in as {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# Main app
if st.session_state.logged_in:
    st.title("Stock Analysis Bot")
    st.write("This bot scraps and gathers real time stock related information and analyzes it using LLM")

    # Query input
    query = st.text_input('Input your investment related query:')
    col1, col2 = st.columns(2)
    
    with col1:
        enter = st.button("Enter")
    with col2:
        clear = st.button("Clear")

    if clear:
        st.markdown(' ')

    if enter and query:
        with st.spinner('Gathering all required information and analyzing.'):
            out = Analyze_stock(query)
            save_query(st.session_state.username, query, out)
        st.success('Done!')
        st.write(out)

    # History section
    st.header("Your Query History")
    history = get_user_history(st.session_state.username)
    
    for query, response, timestamp in history:
        with st.expander(f"Query: {query[:50]}... ({timestamp})"):
            st.write("Query:", query)
            st.write("Response:", response)
            st.write("Time:", timestamp)
else:
    st.title("Welcome to Stock Analysis Bot")
    st.write("Please login or register to continue")
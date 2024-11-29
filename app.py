# app.py
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from tools.fetch_stock_info import Anazlyze_stock

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS queries
                 (username TEXT, query TEXT, response TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

# Security functions
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
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if action == "Register":
            if st.button("Register"):
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute('INSERT OR IGNORE INTO users VALUES (?, ?)', 
                         (username, make_hash(password)))
                conn.commit()
                conn.close()
                st.success("Registration successful!")
                
        else:  # Login
            if st.button("Login"):
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
            out = Anazlyze_stock(query)
            # Save query to database
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
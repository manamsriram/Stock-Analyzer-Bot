import streamlit as st
<<<<<<< Updated upstream
from tools.fetch_stock_info import Anazlyze_stock
=======
import sqlite3
import hashlib
from datetime import datetime
import pika
import json
import threading
from tools.fetch_stock_info import Anazlyze_stock, get_stock_price
>>>>>>> Stashed changes

st.title("Stock Analysis bot")
st.write("This bot scraps and gathers real time stock realted information and analyzes it using LLM")

query = st.text_input('Input your investment related query:') 

Enter=st.button("Enter")
clear=st.button("Clear")

if clear:
    print(clear)
    st.markdown(' ')

<<<<<<< Updated upstream
if Enter:
    with st.spinner('Gathering all required information and analyzing. Be patient!!!!!'):
        out=Anazlyze_stock(query)
    st.success('Done!')
    st.write(out)
=======
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

# RabbitMQ Configuration
class RabbitMQHandler:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='stock_analysis_queue', durable=True)
        self.channel.queue_declare(queue='results_queue', durable=True)
        
    def publish_query(self, username, query):
        message = {
            'username': username,
            'query': query,
            'timestamp': datetime.now().isoformat()
        }
        self.channel.basic_publish(
            exchange='',
            routing_key='stock_analysis_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            )
        )

    def close(self):
        self.connection.close()

# Worker Process
def process_stock_analysis():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        message = json.loads(body)
        try:
            # Process the stock analysis
            result = Anazlyze_stock(message['query'])
            
            # Save to database
            save_query(message['username'], message['query'], result)
            
            # Publish result
            channel.basic_publish(
                exchange='',
                routing_key='results_queue',
                body=json.dumps({
                    'username': message['username'],
                    'result': result,
                    'original_query': message['query']
                })
            )
        except Exception as e:
            print(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='stock_analysis_queue', on_message_callback=callback)
    channel.start_consuming()

# Start worker thread
worker_thread = threading.Thread(target=process_stock_analysis, daemon=True)
worker_thread.start()

# Initialize RabbitMQ handler
rabbitmq = RabbitMQHandler()

# Modified query submission
def submit_query(username, query):
    rabbitmq.publish_query(username, query)
    return "Query submitted for processing"

# Modify the main app section
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
        with st.spinner('Gathering all required information and analyzing. Be patient!!!!!'):
            out = Anazlyze_stock(query)
            save_query(st.session_state.username, query, out)
        st.success('Done!')
        st.write(out)
        
        # Create tabs for different types of information
        tab1, tab2, tab3 = st.tabs(["Analysis", "Market Data"])
        
        with tab1:
            st.markdown("### Analysis Results")
            st.write(out)
            
        with tab2:
            st.markdown("### Market Information")
            st.line_chart(get_stock_price(query))

    # Modified history section with real-time updates
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
>>>>>>> Stashed changes

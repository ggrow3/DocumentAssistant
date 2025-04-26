import streamlit as st
import hashlib
import os
import json
from datetime import datetime, timedelta

# Constants
USER_DB_FILE = ".streamlit/users.json"
SESSION_EXPIRY = 12  # hours

def initialize_auth():
    """Initialize authentication system"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'auth_message' not in st.session_state:
        st.session_state.auth_message = None
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()
    
    # Create users directory if it doesn't exist
    os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
    
    # Create user database file if it doesn't exist
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'w') as f:
            json.dump({"users": []}, f)

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from the database file"""
    try:
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return empty user database if file doesn't exist or is invalid
        return {"users": []}

def save_users(user_data):
    """Save users to the database file"""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(user_data, f, indent=2)

def create_user(username, password, full_name, email, firm_name=None, user_role="user"):
    """Create a new user"""
    # Load existing users
    user_data = load_users()
    
    # Check if username already exists
    if any(user['username'] == username for user in user_data['users']):
        return False, "Username already exists"
    
    # Create new user
    new_user = {
        "username": username,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "email": email,
        "firm_name": firm_name,
        "role": user_role,
        "created_at": datetime.now().isoformat()
    }
    
    # Add to user database
    user_data['users'].append(new_user)
    save_users(user_data)
    
    return True, "User created successfully"

def authenticate(username, password):
    """Authenticate a user"""
    user_data = load_users()
    
    # Find user by username
    user = next((user for user in user_data['users'] if user['username'] == username), None)
    
    if user and user['password_hash'] == hash_password(password):
        # Set session state for authenticated user
        st.session_state.authenticated = True
        st.session_state.current_user = {
            "username": user['username'],
            "full_name": user['full_name'],
            "email": user['email'],
            "firm_name": user.get('firm_name'),
            "role": user.get('role', 'user')
        }
        st.session_state.last_activity = datetime.now()
        return True, "Authentication successful"
    
    return False, "Invalid username or password"

def logout():
    """Log out the current user"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.auth_message = "You have been logged out"

def is_session_expired():
    """Check if the session has expired"""
    if not st.session_state.authenticated:
        return False
    
    now = datetime.now()
    expiry_time = st.session_state.last_activity + timedelta(hours=SESSION_EXPIRY)
    
    if now > expiry_time:
        return True
    
    # Update last activity time
    st.session_state.last_activity = now
    return False

def check_authentication():
    """Check if user is authenticated and session is not expired"""
    if is_session_expired():
        logout()
        st.session_state.auth_message = "Your session has expired. Please log in again."
        return False
    
    return st.session_state.authenticated

def login_form():
    """Display login form"""
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")
        
        if submitted:
            success, message = authenticate(username, password)
            if not success:
                st.error(message)
            else:
                st.session_state.auth_message = f"Welcome, {st.session_state.current_user['full_name']}!"
                st.rerun()

def signup_form():
    """Display sign up form"""
    with st.form("signup_form"):
        st.subheader("Create New Account")
        
        username = st.text_input("Username (required)")
        password = st.text_input("Password (required)", type="password")
        confirm_password = st.text_input("Confirm Password (required)", type="password")
        full_name = st.text_input("Full Name (required)")
        email = st.text_input("Email (required)")
        firm_name = st.text_input("Law Firm Name (optional)")
        
        submitted = st.form_submit_button("Sign Up")
        
        if submitted:
            if not username or not password or not full_name or not email:
                st.error("Please fill in all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = create_user(username, password, full_name, email, firm_name)
                if not success:
                    st.error(message)
                else:
                    st.success(message)
                    st.session_state.auth_message = "Account created successfully. Please log in."
                    st.rerun()

def display_auth_interface():
    """Display the authentication interface"""
    initialize_auth()
    
    if st.session_state.auth_message:
        # Display any authentication messages
        if "error" in st.session_state.auth_message.lower():
            st.error(st.session_state.auth_message)
        elif "success" in st.session_state.auth_message.lower() or "welcome" in st.session_state.auth_message.lower():
            st.success(st.session_state.auth_message)
        else:
            st.info(st.session_state.auth_message)
        
        # Clear the message after displaying it once
        st.session_state.auth_message = None
    
    if not check_authentication():
        # Display login/signup tabs
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            login_form()
        
        with tab2:
            signup_form()
        
        # Stop app execution for unauthenticated users
        st.stop()
    
    # User profile and logout in sidebar
    with st.sidebar:
        if st.session_state.current_user:
            st.sidebar.markdown(f"""
            ### User Profile
            **Name:** {st.session_state.current_user['full_name']}  
            **Username:** {st.session_state.current_user['username']}  
            **Email:** {st.session_state.current_user['email']}
            """)
            
            if st.session_state.current_user.get('firm_name'):
                st.sidebar.markdown(f"**Firm:** {st.session_state.current_user['firm_name']}")
            
            if st.sidebar.button("Log Out"):
                logout()
                st.rerun()

def create_default_admin():
    """Create default admin user if no users exist"""
    user_data = load_users()
    
    if not user_data['users']:
        create_user(
            username="admin",
            password="admin123",  # This should be changed after first login
            full_name="System Administrator",
            email="admin@example.com",
            user_role="admin"
        )
        st.session_state.auth_message = "Default admin user created. Username: admin, Password: admin123"
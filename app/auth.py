import hashlib


def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """Verify a password against its hash"""
    return hash_password(password) == hashed


def login(username, password):
    """Authenticate a user"""
    from app.db import get_user_by_username
    
    try:
        user = get_user_by_username(username)
        if user and verify_password(password, user[2]):  # user[2] is the password field
            return user
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None
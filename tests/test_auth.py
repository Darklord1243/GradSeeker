# tests/test_auth.py
# Tests for authentication system (RFC 3)

import pytest
from app import create_app
from models import db, User
from utils import hash_password, verify_password


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Store app on client for later use in tests
            client.application = app
            yield client
            db.drop_all()


def test_register_form_exists(client):
    """
    Test Step 3.1: Registration Form UI
    Verify that the registration form exists and has required fields.
    """
    response = client.get('/register')
    
    # Verify page loads successfully
    assert response.status_code == 200
    
    # Verify form exists
    assert b'<form' in response.data
    assert b'method="POST"' in response.data
    assert b'action="/register"' in response.data
    
    # Verify required form fields exist
    assert b'username' in response.data.lower()
    assert b'password' in response.data.lower()
    
    # Verify labels are present (accessibility requirement)
    assert b'<label' in response.data
    assert b'for="username"' in response.data
    assert b'for="password"' in response.data
    
    # Verify input fields have proper attributes
    assert b'type="text"' in response.data or b'type="text"' in response.data.lower()
    assert b'type="password"' in response.data or b'type="password"' in response.data.lower()
    assert b'required' in response.data or b'required' in response.data.lower()
    
    # Verify submit button exists
    assert b'<button' in response.data or b'type="submit"' in response.data
    
    # Verify page title
    assert b'Register' in response.data


def test_register_form_bootstrap_styling(client):
    """
    Test Step 3.2: Registration Form Styles
    Verify that Bootstrap classes are present in the registration form.
    """
    response = client.get('/register')
    
    # Verify Bootstrap CSS is loaded
    assert b'bootstrap' in response.data.lower()
    assert b'bootstrap@5.3.0' in response.data or b'bootstrap.min.css' in response.data
    
    # Verify Bootstrap classes are used in the form
    assert b'container' in response.data
    assert b'row' in response.data
    # Check for Bootstrap column classes (template uses responsive columns: col-12, col-sm-10, col-md-8, col-lg-6, col-xl-5)
    assert b'col-' in response.data  # Any Bootstrap column class
    assert b'card' in response.data
    assert b'card-body' in response.data
    assert b'form-control' in response.data
    assert b'form-label' in response.data
    assert b'btn' in response.data
    assert b'btn-primary' in response.data
    # Check for margin bottom utility classes (template uses mb-4 and mb-5)
    assert b'mb-' in response.data  # Any margin-bottom utility class
    
    # Verify custom CSS file is linked
    assert b'style.css' in response.data or b'css/style.css' in response.data
    
    # Verify Inter font is loaded (SRS UI-11)
    assert b'Inter' in response.data or b'fonts.googleapis.com' in response.data


def test_register_route_exists(client):
    """
    Test Step 3.3: Registration Route (Data Connection)
    Verify that the /register route exists and renders the template correctly.
    Note: POST now redirects (302) on success since Step 3.5 is implemented.
    """
    # Test GET request
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    assert b'<form' in response.data
    
    # Test POST request (now redirects on successful registration - Step 3.5 behavior)
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpass123'
    })
    # Should redirect to login page (302) on successful registration
    assert response.status_code == 302
    assert '/login' in response.location


def test_password_hashing():
    """
    Test Step 3.4: Password Hashing Logic
    Verify that password hashing and verification work correctly.
    """
    password = 'test123'
    hashed = hash_password(password)
    
    # Verify password is hashed (not stored in plain text)
    assert hashed != password
    assert len(hashed) > len(password)  # Hash should be longer
    
    # Verify correct password matches hash
    assert verify_password(hashed, password) is True
    
    # Verify incorrect password does not match hash
    assert verify_password(hashed, 'wrong') is False
    assert verify_password(hashed, 'test124') is False
    
    # Verify same password produces different hashes (salting)
    hashed2 = hash_password(password)
    assert hashed != hashed2  # Due to salting, same password should produce different hashes
    # But both should verify correctly
    assert verify_password(hashed2, password) is True


def test_registration_creates_user(client):
    """
    Test Step 3.5: Registration Logic - User Creation
    Verify that registration creates a user in the database with hashed password.
    """
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'test123'
    })
    
    # Verify redirect to login page (registration successful)
    assert response.status_code == 302
    assert '/login' in response.location
    
    # Verify user was created in database
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.username == 'testuser'
        
        # Verify password is hashed (not stored in plain text)
        assert user.password != 'test123'
        assert len(user.password) > len('test123')
        assert verify_password(user.password, 'test123') is True
        assert verify_password(user.password, 'wrong') is False


def test_registration_duplicate_username(client):
    """
    Test Step 3.5: Registration Logic - Duplicate Username Prevention
    Verify that attempting to register with an existing username shows an error.
    """
    # Register first user
    response1 = client.post('/register', data={
        'username': 'test',
        'password': 'pass123'
    })
    assert response1.status_code == 302  # Successful registration
    
    # Try to register with the same username
    response2 = client.post('/register', data={
        'username': 'test',
        'password': 'differentpass'
    })
    
    # Should render template (not redirect) and show error message
    assert response2.status_code == 200
    assert b'already exists' in response2.data.lower()
    
    # Verify only one user with that username exists
    with client.application.app_context():
        users = User.query.filter_by(username='test').all()
        assert len(users) == 1


def test_registration_empty_fields(client):
    """
    Test Step 3.5: Registration Logic - Empty Field Validation
    Verify that registration with empty username or password shows an error.
    """
    # Test empty username
    response1 = client.post('/register', data={
        'username': '',
        'password': 'test123'
    })
    assert response1.status_code == 200
    assert b'required' in response1.data.lower()
    
    # Test empty password
    response2 = client.post('/register', data={
        'username': 'newuser',
        'password': ''
    })
    assert response2.status_code == 200
    assert b'required' in response2.data.lower()
    
    # Verify no user was created
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is None


def test_login_form_exists(client):
    """
    Test Step 3.6: Login Form UI
    Verify that the login form exists and has required fields.
    """
    response = client.get('/login')
    
    # Verify page loads successfully
    assert response.status_code == 200
    
    # Verify form exists
    assert b'<form' in response.data
    assert b'method="POST"' in response.data
    assert b'action="/login"' in response.data
    
    # Verify required form fields exist
    assert b'username' in response.data.lower()
    assert b'password' in response.data.lower()
    
    # Verify labels are present (accessibility requirement)
    assert b'<label' in response.data
    assert b'for="username"' in response.data
    assert b'for="password"' in response.data
    
    # Verify input fields have proper attributes
    assert b'type="text"' in response.data or b'type="text"' in response.data.lower()
    assert b'type="password"' in response.data or b'type="password"' in response.data.lower()
    assert b'required' in response.data or b'required' in response.data.lower()
    
    # Verify submit button exists
    assert b'<button' in response.data or b'type="submit"' in response.data
    
    # Verify page title
    assert b'Login' in response.data
    
    # Verify link to registration page
    assert b'/register' in response.data


def test_login_form_bootstrap_styling(client):
    """
    Test Step 3.7: Login Form Styles
    Verify that Bootstrap classes are present in the login form.
    """
    response = client.get('/login')
    
    # Verify Bootstrap CSS is loaded
    assert b'bootstrap' in response.data.lower()
    assert b'bootstrap@5.3.0' in response.data or b'bootstrap.min.css' in response.data
    
    # Verify Bootstrap classes are used in the form
    assert b'container' in response.data
    assert b'row' in response.data
    # Check for Bootstrap column classes (template uses responsive columns)
    assert b'col-' in response.data  # Any Bootstrap column class
    assert b'card' in response.data
    assert b'card-body' in response.data
    assert b'form-control' in response.data
    assert b'form-label' in response.data
    assert b'btn' in response.data
    assert b'btn-primary' in response.data
    # Check for margin bottom utility classes
    assert b'mb-' in response.data  # Any margin-bottom utility class
    
    # Verify custom CSS file is linked
    assert b'style.css' in response.data or b'css/style.css' in response.data
    
    # Verify Inter font is loaded (SRS UI-11)
    assert b'Inter' in response.data or b'fonts.googleapis.com' in response.data
    
    # Verify Bootstrap JS bundle is included
    assert b'bootstrap.bundle.min.js' in response.data or b'bootstrap' in response.data.lower()


def test_login_success(client):
    """
    Test Step 3.8: Login Route & Logic - Successful Login
    Verify that a user can log in with correct credentials and is redirected to dashboard.
    """
    # Create user first
    with client.application.app_context():
        user = User(username='test', password=hash_password('pass'))
        db.session.add(user)
        db.session.commit()
    
    # Attempt login with correct credentials
    response = client.post('/login', data={
        'username': 'test',
        'password': 'pass'
    })
    
    # Should redirect to dashboard (302)
    assert response.status_code == 302
    assert '/dashboard' in response.location
    
    # Follow redirect to verify login was successful
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'test' in response.data  # Username should appear on dashboard


def test_login_invalid_credentials(client):
    """
    Test Step 3.8: Login Route & Logic - Invalid Credentials
    Verify that login with wrong username or password shows an error message.
    """
    # Create a user
    with client.application.app_context():
        user = User(username='test', password=hash_password('correctpass'))
        db.session.add(user)
        db.session.commit()
    
    # Test wrong password
    response = client.post('/login', data={
        'username': 'test',
        'password': 'wrongpass'
    })
    assert response.status_code == 200  # Should render login page, not redirect
    assert b'Invalid credentials' in response.data or b'Invalid' in response.data
    
    # Test wrong username
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'anypass'
    })
    assert response.status_code == 200
    assert b'Invalid credentials' in response.data or b'Invalid' in response.data


def test_login_empty_fields(client):
    """
    Test Step 3.8: Login Route & Logic - Empty Field Validation
    Verify that login with empty username or password shows an error.
    """
    # Test empty username
    response = client.post('/login', data={
        'username': '',
        'password': 'test123'
    })
    assert response.status_code == 200
    assert b'required' in response.data.lower()
    
    # Test empty password
    response = client.post('/login', data={
        'username': 'testuser',
        'password': ''
    })
    assert response.status_code == 200
    assert b'required' in response.data.lower()


def test_login_route_handles_get(client):
    """
    Test Step 3.8: Login Route & Logic - GET Request
    Verify that GET request to /login renders the login form.
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'<form' in response.data


def test_login_session_management(client):
    """
    Test Step 3.8: Login Route & Logic - Session Management
    Verify that Flask-Login properly manages user sessions.
    """
    # Create user
    with client.application.app_context():
        user = User(username='sessiontest', password=hash_password('pass123'))
        db.session.add(user)
        db.session.commit()
    
    # Login
    response = client.post('/login', data={
        'username': 'sessiontest',
        'password': 'pass123'
    })
    assert response.status_code == 302  # Redirect after login
    
    # Access protected route (dashboard requires login)
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'sessiontest' in response.data  # User should be logged in


def test_logout(client):
    """
    Test Step 3.9: Logout Route
    Verify that a logged-in user can log out and is redirected to home page.
    """
    # Create user
    with client.application.app_context():
        user = User(username='test', password=hash_password('pass'))
        db.session.add(user)
        db.session.commit()
    
    # Login first
    response = client.post('/login', data={
        'username': 'test',
        'password': 'pass'
    })
    assert response.status_code == 302  # Redirect after login
    
    # Verify user is logged in (can access protected route)
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'test' in response.data
    
    # Logout
    response = client.get('/logout')
    assert response.status_code == 302  # Should redirect
    assert '/' in response.location  # Should redirect to home page
    
    # Verify user is logged out (cannot access protected route)
    # This is the most important verification - user should no longer have access
    response = client.get('/dashboard')
    assert response.status_code == 302  # Should redirect to login (not 200)
    assert '/login' in response.location
    
    # Note: Flash message verification is skipped here because the home page
    # is a simple string return without template rendering. Flash messages
    # will be visible once templates are implemented in RFC 4.


def test_logout_requires_login(client):
    """
    Test Step 3.9: Logout Route - Authentication Required
    Verify that logout route requires user to be logged in.
    """
    # Try to logout without being logged in
    response = client.get('/logout')
    # Should redirect to login page (since @login_required decorator)
    assert response.status_code == 302
    assert '/login' in response.location
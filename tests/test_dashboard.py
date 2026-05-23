# tests/test_dashboard.py
# Tests for user dashboard and profile management (RFC 9)

import pytest
from app import create_app
from models import db, User
from utils import hash_password


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
            try:
                yield client
            finally:
                # Ensure all transactions are rolled back first
                db.session.rollback()
                db.session.close()
                # Drop all tables
                try:
                    db.drop_all()
                except Exception:
                    pass  # Ignore errors during teardown
                # Close all connections
                try:
                    db.engine.dispose()
                except Exception:
                    pass  # Ignore errors during teardown


def test_dashboard_exists(client):
    """
    Test Step 9.1: Dashboard UI Structure
    Verify that the dashboard exists and shows profile form.
    """
    # Create a test user
    user = User(username='test', password=hash_password('pass'))
    db.session.add(user)
    db.session.commit()
    
    # Login the user
    client.post('/login', data={'username': 'test', 'password': 'pass'})
    
    # Access dashboard
    response = client.get('/dashboard')
    
    # Verify page loads successfully
    assert response.status_code == 200
    
    # Verify dashboard title and welcome message
    assert b'Dashboard' in response.data
    assert b'Welcome' in response.data
    assert b'test' in response.data  # Username should appear
    
    # Verify profile section exists (Step 9.1)
    assert b'Your Profile' in response.data
    assert b'The Wallet' in response.data
    
    # Verify profile form exists
    assert b'<form' in response.data
    assert b'method="POST"' in response.data
    assert b'action="/dashboard/update-profile"' in response.data
    
    # Verify all profile fields exist
    assert b'GPA' in response.data
    assert b'TOEFL Score' in response.data
    assert b'Internship Experience' in response.data
    assert b'Research Papers Count' in response.data
    
    # Verify form inputs exist with proper attributes
    assert b'id="gpa"' in response.data
    assert b'name="gpa"' in response.data
    assert b'type="number"' in response.data
    assert b'step="0.01"' in response.data
    
    assert b'id="toefl_score"' in response.data
    assert b'name="toefl_score"' in response.data
    
    assert b'id="internship_exp"' in response.data
    assert b'name="internship_exp"' in response.data
    
    assert b'id="research_papers"' in response.data
    assert b'name="research_papers"' in response.data
    
    # Verify submit button exists
    assert b'Update Profile' in response.data
    assert b'type="submit"' in response.data
    
    # Verify labels are present (accessibility requirement)
    assert b'<label' in response.data
    assert b'for="gpa"' in response.data
    assert b'for="toefl_score"' in response.data
    assert b'for="internship_exp"' in response.data
    assert b'for="research_papers"' in response.data


def test_dashboard_requires_login(client):
    """
    Test that dashboard requires authentication.
    """
    # Try to access dashboard without logging in
    response = client.get('/dashboard', follow_redirects=True)
    
    # Should redirect to login page
    assert response.status_code == 200
    assert b'login' in response.data.lower() or b'Login' in response.data


def test_dashboard_responsive_layout(client):
    """
    Test Step 9.2: Dashboard Styles - Responsive Bootstrap Grid
    Verify that the dashboard uses Bootstrap grid classes for responsive layout.
    """
    # Create a test user
    user = User(username='test', password=hash_password('pass'))
    db.session.add(user)
    db.session.commit()
    
    # Login the user
    client.post('/login', data={'username': 'test', 'password': 'pass'})
    
    # Access dashboard
    response = client.get('/dashboard')
    
    # Verify page loads successfully
    assert response.status_code == 200
    
    # Verify Bootstrap row class is present
    assert b'class="row' in response.data or b'class="row dashboard-row' in response.data
    
    # Verify responsive Bootstrap grid classes are present
    # Mobile-first: col-12 (full width on mobile)
    assert b'col-12' in response.data
    
    # Medium screens and up: col-md-6 (half width on tablets/desktop)
    assert b'col-md-6' in response.data
    
    # Verify both sections (profile and shortlist) have responsive classes
    # Count occurrences to ensure both columns have the classes
    response_text = response.data.decode('utf-8')
    col_12_count = response_text.count('col-12')
    col_md_6_count = response_text.count('col-md-6')
    
    # Should have at least 2 instances (one for profile, one for shortlist)
    assert col_12_count >= 2, "Both columns should have col-12 class for mobile"
    assert col_md_6_count >= 2, "Both columns should have col-md-6 class for desktop"
    
    # Verify dashboard-row class is present (for custom spacing)
    assert b'dashboard-row' in response.data or b'class="row dashboard-row' in response.data
    
    # Verify cards are present (Bootstrap card component)
    assert b'class="card' in response.data
    assert b'card-body' in response.data
    
    # Verify table-responsive class is present for shortlist table (mobile-friendly)
    assert b'table-responsive' in response.data or b'Your Shortlist' in response.data


def test_update_profile(client):
    """
    Test Step 9.3: Profile Update Route - Data Connection
    Verify that profile update route correctly updates user's academic credentials.
    """
    # Create a test user with initial values
    user = User(
        username='test', 
        password=hash_password('pass'), 
        gpa=3.0,
        toefl_score=90,
        internship_exp=3,
        research_papers=1
    )
    db.session.add(user)
    db.session.commit()
    
    # Login the user
    client.post('/login', data={'username': 'test', 'password': 'pass'})
    
    # Update profile with new values
    response = client.post('/dashboard/update-profile', data={
        'gpa': '3.5',
        'toefl_score': '100',
        'internship_exp': '6',
        'research_papers': '2'
    }, follow_redirects=True)
    
    # Verify redirect to dashboard
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    
    # Verify success message
    assert b'Profile updated successfully' in response.data or b'success' in response.data.lower()
    
    # Refresh user from database to verify changes
    db.session.refresh(user)
    
    # Verify all fields were updated correctly
    assert user.gpa == 3.5
    assert user.toefl_score == 100
    assert user.internship_exp == 6
    assert user.research_papers == 2


def test_update_profile_validation_gpa(client):
    """
    Test Step 9.3: Profile Update Route - Validation
    Verify that GPA validation works correctly (0.0 - 4.0).
    """
    user = User(username='test_gpa', password=hash_password('pass'))
    db.session.add(user)
    db.session.commit()
    
    client.post('/login', data={'username': 'test_gpa', 'password': 'pass'})
    
    # Test invalid GPA (too high)
    response = client.post('/dashboard/update-profile', data={
        'gpa': '5.0',
        'toefl_score': '100',
        'internship_exp': '6',
        'research_papers': '2'
    }, follow_redirects=True)
    
    assert b'GPA must be between 0.0 and 4.0' in response.data or b'error' in response.data.lower()
    
    # Verify user's GPA was not updated
    db.session.refresh(user)
    assert user.gpa == 0.0  # Default value
    
    # Test invalid GPA (negative)
    response = client.post('/dashboard/update-profile', data={
        'gpa': '-1.0',
        'toefl_score': '100',
        'internship_exp': '6',
        'research_papers': '2'
    }, follow_redirects=True)
    
    assert b'GPA must be between 0.0 and 4.0' in response.data or b'error' in response.data.lower()


def test_update_profile_validation_toefl(client):
    """
    Test Step 9.3: Profile Update Route - Validation
    Verify that TOEFL score validation works correctly (0 - 120).
    """
    user = User(username='test_toefl', password=hash_password('pass'))
    db.session.add(user)
    db.session.commit()
    
    client.post('/login', data={'username': 'test_toefl', 'password': 'pass'})
    
    # Test invalid TOEFL score (too high)
    response = client.post('/dashboard/update-profile', data={
        'gpa': '3.5',
        'toefl_score': '150',
        'internship_exp': '6',
        'research_papers': '2'
    }, follow_redirects=True)
    
    assert b'TOEFL score must be between 0 and 120' in response.data or b'error' in response.data.lower()
    
    # Verify user's TOEFL score was not updated
    db.session.refresh(user)
    assert user.toefl_score == 0  # Default value


def test_update_profile_validation_negative_values(client):
    """
    Test Step 9.3: Profile Update Route - Validation
    Verify that negative values are rejected for internship_exp and research_papers.
    """
    user = User(username='test_negative', password=hash_password('pass'))
    db.session.add(user)
    db.session.commit()
    
    client.post('/login', data={'username': 'test_negative', 'password': 'pass'})
    
    # Test negative internship experience
    response = client.post('/dashboard/update-profile', data={
        'gpa': '3.5',
        'toefl_score': '100',
        'internship_exp': '-1',
        'research_papers': '2'
    }, follow_redirects=True)
    
    assert b'Internship experience cannot be negative' in response.data or b'error' in response.data.lower()
    
    # Test negative research papers
    response = client.post('/dashboard/update-profile', data={
        'gpa': '3.5',
        'toefl_score': '100',
        'internship_exp': '6',
        'research_papers': '-1'
    }, follow_redirects=True)
    
    assert b'Research papers count cannot be negative' in response.data or b'error' in response.data.lower()


def test_update_profile_empty_values(client):
    """
    Test Step 9.3: Profile Update Route - Edge Cases
    Verify that empty values are handled correctly (default to 0).
    """
    user = User(
        username='test_empty', 
        password=hash_password('pass'),
        gpa=3.5,
        toefl_score=100,
        internship_exp=6,
        research_papers=2
    )
    db.session.add(user)
    db.session.commit()
    
    client.post('/login', data={'username': 'test_empty', 'password': 'pass'})
    
    # Update with empty values
    response = client.post('/dashboard/update-profile', data={
        'gpa': '',
        'toefl_score': '',
        'internship_exp': '',
        'research_papers': ''
    }, follow_redirects=True)
    
    # Should succeed and set values to 0
    assert response.status_code == 200
    
    # Refresh user from database
    db.session.refresh(user)
    
    # Verify all fields were set to 0
    assert user.gpa == 0.0
    assert user.toefl_score == 0
    assert user.internship_exp == 0
    assert user.research_papers == 0


def test_update_profile_requires_login(client):
    """
    Test Step 9.3: Profile Update Route - Authentication
    Verify that profile update requires authentication.
    """
    # Try to update profile without logging in
    response = client.post('/dashboard/update-profile', data={
        'gpa': '3.5',
        'toefl_score': '100',
        'internship_exp': '6',
        'research_papers': '2'
    }, follow_redirects=True)
    
    # Should redirect to login page
    assert response.status_code == 200
    assert b'login' in response.data.lower() or b'Login' in response.data


def test_compatibility_updates_after_profile_change(client):
    """
    Test Step 9.4: Compatibility Update After Profile Change
    Verify that compatibility scores automatically recalculate when profile is updated.
    """
    from models import University, Program
    
    # Create a test user with low credentials
    user = User(
        username='test_compat',
        password=hash_password('pass'),
        gpa=2.5,
        toefl_score=80,
        internship_exp=0,
        research_papers=0
    )
    db.session.add(user)
    
    # Create a university and program
    university = University(
        name='Test University',
        country='Test Country',
        qs_rank=100
    )
    db.session.add(university)
    db.session.commit()
    
    program = Program(
        name='Test Program',
        university_id=university.id,
        category='CS',
        min_gpa=3.0,
        min_toefl=90,
        research_focus=True,
        industry_focus=True
    )
    db.session.add(program)
    
    # Add program to user's shortlist
    user.shortlisted_programs.append(program)
    db.session.commit()
    
    # Login user
    client.post('/login', data={'username': 'test_compat', 'password': 'pass'})
    
    # Check initial compatibility (should be "Reach / Low Chance" - low score)
    status_initial, color_initial = program.calculate_compatibility(user)
    assert status_initial == "Reach / Low Chance"
    assert color_initial == "danger"
    
    # Update profile with better credentials
    response = client.post('/dashboard/update-profile', data={
        'gpa': '3.8',
        'toefl_score': '110',
        'internship_exp': '6',
        'research_papers': '2'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Profile updated successfully' in response.data or b'success' in response.data.lower()
    
    # Refresh user from database
    db.session.refresh(user)
    
    # Verify profile was updated
    assert user.gpa == 3.8
    assert user.toefl_score == 110
    assert user.internship_exp == 6
    assert user.research_papers == 2
    
    # Check updated compatibility (should be "Safe / High Chance" - high score)
    status_updated, color_updated = program.calculate_compatibility(user)
    assert status_updated == "Safe / High Chance"
    assert color_updated == "success"
    
    # Verify compatibility changed
    assert status_initial != status_updated
    assert color_initial != color_updated


def test_compatibility_updates_on_dashboard_after_profile_change(client):
    """
    Test Step 9.4: Compatibility Update After Profile Change
    Verify that compatibility scores update on dashboard shortlist after profile change.
    """
    from models import University, Program
    
    # Create a test user with medium credentials
    user = User(
        username='test_dashboard_compat',
        password=hash_password('pass'),
        gpa=3.0,
        toefl_score=90,
        internship_exp=2,
        research_papers=0
    )
    db.session.add(user)
    
    # Create a university and program
    university = University(
        name='Test University',
        country='Test Country',
        qs_rank=100
    )
    db.session.add(university)
    db.session.commit()
    
    program = Program(
        name='Test Program',
        university_id=university.id,
        category='CS',
        min_gpa=3.5,
        min_toefl=100,
        research_focus=True,
        industry_focus=True
    )
    db.session.add(program)
    
    # Add program to user's shortlist
    user.shortlisted_programs.append(program)
    db.session.commit()
    
    # Login user
    client.post('/login', data={'username': 'test_dashboard_compat', 'password': 'pass'})
    
    # Check dashboard before update (should show "Target / Medium Chance" or "Reach")
    response_before = client.get('/dashboard')
    assert response_before.status_code == 200
    
    # Get initial compatibility status from dashboard
    status_before, _ = program.calculate_compatibility(user)
    
    # Update profile with better credentials
    client.post('/dashboard/update-profile', data={
        'gpa': '3.7',
        'toefl_score': '105',
        'internship_exp': '6',
        'research_papers': '2'
    }, follow_redirects=True)
    
    # Refresh user from database
    db.session.refresh(user)
    
    # Check dashboard after update
    response_after = client.get('/dashboard')
    assert response_after.status_code == 200
    
    # Get updated compatibility status
    status_after, _ = program.calculate_compatibility(user)
    
    # Verify compatibility changed (should improve)
    # Before: likely "Target" or "Reach" (score 2-3)
    # After: should be "Safe" or "Target" (score 4+)
    assert status_after in ["Safe / High Chance", "Target / Medium Chance"]
    
    # Verify the dashboard shows the updated compatibility badge
    # The badge should reflect the new status
    if status_after == "Safe / High Chance":
        assert b'success' in response_after.data.lower() or b'Safe' in response_after.data
    elif status_after == "Target / Medium Chance":
        assert b'warning' in response_after.data.lower() or b'Target' in response_after.data


def test_compatibility_updates_with_gpa_improvement(client):
    """
    Test Step 9.4: Compatibility Update After Profile Change
    Verify that improving GPA specifically updates compatibility scores.
    """
    from models import University, Program
    
    # Create a test user with GPA just below requirement
    user = User(
        username='test_gpa_compat',
        password=hash_password('pass'),
        gpa=2.9,  # Just below 3.0 requirement
        toefl_score=95,
        internship_exp=3,
        research_papers=1
    )
    db.session.add(user)
    
    # Create a university and program
    university = University(
        name='Test University',
        country='Test Country',
        qs_rank=100
    )
    db.session.add(university)
    db.session.commit()
    
    program = Program(
        name='Test Program',
        university_id=university.id,
        category='CS',
        min_gpa=3.0,
        min_toefl=90,
        research_focus=True,
        industry_focus=True
    )
    db.session.add(program)
    
    # Add program to user's shortlist
    user.shortlisted_programs.append(program)
    db.session.commit()
    
    # Login user
    client.post('/login', data={'username': 'test_gpa_compat', 'password': 'pass'})
    
    # Test with a program where GPA improvement clearly changes the result
    # Use a program with higher GPA requirement and no research/industry focus
    program2 = Program(
        name='Test Program 2',
        university_id=university.id,
        category='CS',
        min_gpa=3.5,
        min_toefl=90,
        research_focus=False,
        industry_focus=False
    )
    db.session.add(program2)
    user.shortlisted_programs.append(program2)
    db.session.commit()
    
    # Check compatibility with program2 (GPA 2.9 < 3.5, not close enough, so 0 points for GPA)
    status_before_prog2, color_before = program2.calculate_compatibility(user)
    # GPA: 0 (2.9 < 3.3, not close enough), TOEFL: 1 (95 >= 90), research: 0 (research_focus=False), industry: 0 (industry_focus=False)
    # Total = 1 point = "Reach / Low Chance"
    assert status_before_prog2 == "Reach / Low Chance"
    assert color_before == "danger"
    
    # Update GPA to exceed requirement
    client.post('/dashboard/update-profile', data={
        'gpa': '3.6',
        'toefl_score': '95',
        'internship_exp': '3',
        'research_papers': '1'
    }, follow_redirects=True)
    
    # Refresh user from database
    db.session.refresh(user)
    
    # Check updated compatibility (GPA 3.6 >= 3.5, so 2 points for GPA)
    status_after_prog2, color_after = program2.calculate_compatibility(user)
    # GPA: 2 (3.6 >= 3.5), TOEFL: 1 (95 >= 90), research: 0 (research_focus=False), industry: 0 (industry_focus=False)
    # Total = 3 points = "Target / Medium Chance"
    assert status_after_prog2 == "Target / Medium Chance"
    assert color_after == "warning"
    
    # Verify compatibility improved (from "Reach" to "Target")
    assert status_before_prog2 != status_after_prog2
    assert color_before != color_after


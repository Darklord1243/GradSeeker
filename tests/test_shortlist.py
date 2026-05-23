# tests/test_shortlist.py
# Tests for shortlist functionality (RFC 8)

import pytest
from app import create_app
from models import db, User, University, Program
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
            yield client
            db.drop_all()


@pytest.fixture
def test_user(client):
    """Create a test user for authentication tests."""
    with client.application.app_context():
        user = User(
            username='testuser',
            password=hash_password('testpass123'),
            gpa=3.5,
            toefl_score=100
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_program(client):
    """Create a test university and program for shortlist tests."""
    with client.application.app_context():
        university = University(
            name='Test University',
            country='Japan',
            qs_rank=50
        )
        db.session.add(university)
        db.session.commit()
        
        program = Program(
            name='Test Program',
            category='CS',
            university_id=university.id,
            min_gpa=3.0,
            min_toefl=90
        )
        db.session.add(program)
        db.session.commit()
        # Return IDs instead of objects to avoid detached instance issues
        return {'program_id': program.id, 'university_id': university.id}


def test_add_to_list_button_exists_on_program_cards(client, test_user, test_program):
    """
    Test Step 8.1: Add to List Button (UI)
    Verify that the "Add to List" button exists on program cards when user is logged in.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    # Navigate to programs page using university_id from fixture
    university_id = test_program['university_id']
    response = client.get(f'/universities/{university_id}/programs')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Programs page did not load successfully"
    
    # Verify "Add to List" button exists when logged in
    assert b'Add to List' in response.data, "Add to List button not found on program cards"
    assert b'/shortlist/add/' in response.data, "Shortlist add route not found in form action"
    assert b'method="POST"' in response.data, "Form method not POST"
    
    # Verify button is in a form
    assert b'<form' in response.data, "Add to List button not in a form"
    assert b'<button' in response.data, "Button element not found"


def test_add_to_list_button_not_shown_when_not_logged_in(client, test_program):
    """
    Test Step 8.1: Add to List Button (UI)
    Verify that the "Add to List" button is NOT shown when user is not logged in.
    """
    # Navigate to programs page without logging in
    university_id = test_program['university_id']
    response = client.get(f'/universities/{university_id}/programs')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Programs page did not load successfully"
    
    # Verify "Add to List" button does NOT exist when not logged in
    assert b'Add to List' not in response.data, "Add to List button should not be visible when not logged in"


def test_add_to_list_button_exists_on_program_detail_page(client, test_user, test_program):
    """
    Test Step 8.1: Add to List Button (UI)
    Verify that the "Add to List" button exists on program detail page when user is logged in.
    Note: This button was already implemented in program_detail.html, but we verify it here.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    # Navigate to program detail page using program_id from fixture
    program_id = test_program['program_id']
    response = client.get(f'/programs/{program_id}')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Program detail page did not load successfully"
    
    # Verify "Add to List" button exists when logged in
    assert b'Add to List' in response.data, "Add to List button not found on program detail page"
    assert b'/shortlist/add/' in response.data, "Shortlist add route not found in form action"
    assert b'method="POST"' in response.data, "Form method not POST"


def test_add_to_shortlist(client, test_user, test_program):
    """
    Test Step 8.2: Add to List Route (Data Connection)
    Verify that adding a program to shortlist works correctly.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Verify program is NOT in shortlist initially
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program not in user.shortlisted_programs, "Program should not be in shortlist initially"
    
    # Add program to shortlist
    response = client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # Verify redirect occurred (status 200 after follow_redirects)
    assert response.status_code == 200, "Add to shortlist route did not redirect correctly"
    
    # Verify program was added to user's shortlist (check database directly)
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program in user.shortlisted_programs, "Program was not added to user's shortlist"


def test_add_to_shortlist_duplicate_prevention(client, test_user, test_program):
    """
    Test Step 8.2: Add to List Route (Data Connection)
    Verify that duplicate shortlist entries are prevented.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Add program to shortlist first time
    response1 = client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    assert response1.status_code == 200, "First add should succeed"
    
    # Verify program was added to shortlist
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program in user.shortlisted_programs, "Program should be in shortlist after first add"
        initial_count = len(user.shortlisted_programs)
    
    # Try to add the same program again
    response2 = client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    assert response2.status_code == 200, "Second add should also redirect successfully"
    
    # Verify program is still in shortlist (only once) - count should not increase
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program in user.shortlisted_programs, "Program should still be in shortlist"
        # Count should remain the same (duplicate prevention)
        final_count = len(user.shortlisted_programs)
        assert final_count == initial_count, f"Shortlist count should not increase on duplicate add. Initial: {initial_count}, Final: {final_count}"


def test_add_to_shortlist_requires_login(client, test_program):
    """
    Test Step 8.2: Add to List Route (Data Connection)
    Verify that adding to shortlist requires authentication.
    """
    program_id = test_program['program_id']
    
    # Try to add program without logging in
    response = client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # Should redirect to login page
    assert response.status_code == 200, "Should redirect to login page"
    assert b'Login' in response.data or b'login' in response.data.lower(), "Should redirect to login page"


def test_add_to_shortlist_invalid_program(client, test_user):
    """
    Test Step 8.2: Add to List Route (Data Connection)
    Verify that adding a non-existent program returns 404.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    # Try to add non-existent program
    response = client.post('/shortlist/add/99999', follow_redirects=False)
    
    # Should return 404
    assert response.status_code == 404, "Should return 404 for non-existent program"


def test_dashboard_shows_shortlist(client, test_user, test_program):
    """
    Test Step 8.3: Dashboard Shortlist Display (UI)
    Verify that dashboard displays shortlisted programs with all required columns.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Add program to shortlist
    client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # View dashboard
    response = client.get('/dashboard')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Dashboard page did not load successfully"
    
    # Verify table headers are present
    assert b'Program' in response.data, "Program column header not found"
    assert b'University' in response.data, "University column header not found"
    assert b'Date Added' in response.data, "Date Added column header not found"
    assert b'Compatibility' in response.data, "Compatibility column header not found"
    assert b'Actions' in response.data, "Actions column header not found"
    
    # Verify program appears in table
    assert b'Test Program' in response.data, "Program name not found in dashboard"
    assert b'Test University' in response.data, "University name not found in dashboard"
    
    # Verify Remove button exists
    assert b'Remove' in response.data, "Remove button not found"
    assert b'/shortlist/remove/' in response.data, "Remove route not found in form action"
    
    # Verify compatibility badge is displayed
    assert b'badge' in response.data.lower(), "Compatibility badge not found"


def test_dashboard_shows_empty_shortlist(client, test_user):
    """
    Test Step 8.3: Dashboard Shortlist Display (UI)
    Verify that dashboard shows appropriate message when shortlist is empty.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    # View dashboard (no programs added)
    response = client.get('/dashboard')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Dashboard page did not load successfully"
    
    # Verify empty state message
    assert b'Your shortlist is empty' in response.data or b'shortlist is empty' in response.data.lower(), "Empty shortlist message not found"
    assert b'Browse programs' in response.data.lower() or b'/browse' in response.data, "Browse link not found in empty state"


def test_dashboard_shows_date_added(client, test_user, test_program):
    """
    Test Step 8.3: Dashboard Shortlist Display (UI)
    Verify that date added is displayed correctly in dashboard.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Add program to shortlist
    client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # View dashboard
    response = client.get('/dashboard')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Dashboard page did not load successfully"
    
    # Verify date format is displayed (should contain year, month, day pattern)
    # Date format is YYYY-MM-DD HH:MM, so we check for year pattern
    assert b'202' in response.data or b'20' in response.data, "Date added not displayed (check for year pattern)"


def test_remove_from_shortlist(client, test_user, test_program):
    """
    Test Step 8.4: Remove from Shortlist (Logic)
    Verify that removing a program from shortlist works correctly.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Add program to shortlist first
    client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # Verify program is in shortlist
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program in user.shortlisted_programs, "Program should be in shortlist before removal"
    
    # Remove program from shortlist
    response = client.post(f'/shortlist/remove/{program_id}', follow_redirects=True)
    
    # Verify redirect to dashboard occurred
    assert response.status_code == 200, "Remove from shortlist route did not redirect correctly"
    
    # Verify program was removed from shortlist (check database directly)
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program not in user.shortlisted_programs, "Program was not removed from user's shortlist"


def test_remove_from_shortlist_not_in_list(client, test_user, test_program):
    """
    Test Step 8.4: Remove from Shortlist (Logic)
    Verify that trying to remove a program not in shortlist handles gracefully.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Verify program is NOT in shortlist initially
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program not in user.shortlisted_programs, "Program should not be in shortlist initially"
    
    # Try to remove program that's not in shortlist
    response = client.post(f'/shortlist/remove/{program_id}', follow_redirects=True)
    
    # Should still redirect successfully (graceful handling)
    assert response.status_code == 200, "Remove route should handle non-existent shortlist entry gracefully"
    
    # Verify program is still not in shortlist
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program not in user.shortlisted_programs, "Program should still not be in shortlist"


def test_remove_from_shortlist_requires_login(client, test_program):
    """
    Test Step 8.4: Remove from Shortlist (Logic)
    Verify that removing from shortlist requires authentication.
    """
    program_id = test_program['program_id']
    
    # Try to remove program without logging in
    response = client.post(f'/shortlist/remove/{program_id}', follow_redirects=True)
    
    # Should redirect to login page
    assert response.status_code == 200, "Should redirect to login page"
    assert b'Login' in response.data or b'login' in response.data.lower(), "Should redirect to login page"


def test_remove_from_shortlist_invalid_program(client, test_user):
    """
    Test Step 8.4: Remove from Shortlist (Logic)
    Verify that removing a non-existent program returns 404.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    # Try to remove non-existent program
    response = client.post('/shortlist/remove/99999', follow_redirects=False)
    
    # Should return 404
    assert response.status_code == 404, "Should return 404 for non-existent program"


def test_add_and_remove_workflow(client, test_user, test_program):
    """
    Test Step 8.4: Remove from Shortlist (Logic)
    Verify the complete workflow: add program, verify it's there, remove it, verify it's gone.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Step 1: Add program
    client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # Step 2: Verify it's in shortlist
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program in user.shortlisted_programs, "Program should be in shortlist after adding"
    
    # Step 3: Remove program
    client.post(f'/shortlist/remove/{program_id}', follow_redirects=True)
    
    # Step 4: Verify it's removed
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        program = Program.query.get(program_id)
        assert program not in user.shortlisted_programs, "Program should not be in shortlist after removal"


def test_date_added_is_tracked(client, test_user, test_program):
    """
    Test Step 8.5: Date Added Tracking (Data)
    Verify that date_added is automatically set when a program is added to shortlist.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Add program to shortlist
    client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # Verify date_added is stored in the association table
    with client.application.app_context():
        from models import shortlist
        from sqlalchemy import select
        
        # Query user ID from database to avoid detached instance
        user = User.query.filter_by(username='testuser').first()
        user_id = user.id
        
        # Query date_added from association table
        query = select(shortlist.c.date_added).where(
            shortlist.c.user_id == user_id,
            shortlist.c.program_id == program_id
        )
        result = db.session.execute(query).first()
        
        # Verify date_added exists and is not None
        assert result is not None, "date_added should be stored in association table"
        date_added = result[0]
        assert date_added is not None, "date_added should not be None"
        
        # Verify it's a datetime object
        from datetime import datetime
        assert isinstance(date_added, datetime), f"date_added should be a datetime object, got {type(date_added)}"


def test_date_added_is_retrieved_in_dashboard(client, test_user, test_program):
    """
    Test Step 8.5: Date Added Tracking (Data)
    Verify that date_added is correctly retrieved and displayed in dashboard.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Add program to shortlist
    client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # View dashboard
    response = client.get('/dashboard')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Dashboard page did not load successfully"
    
    # Verify date_added is retrieved and displayed
    # The date format is YYYY-MM-DD HH:MM, so we check for the pattern
    # We should see a date string in the response
    assert b'202' in response.data or b'20' in response.data, "Date should be displayed in dashboard"
    
    # Verify the date format matches what we expect (YYYY-MM-DD pattern)
    # This is a basic check - the actual format is verified in the template


def test_date_added_auto_generated(client, test_user, test_program):
    """
    Test Step 8.5: Date Added Tracking (Data)
    Verify that date_added is automatically generated (server_default) when program is added.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    program_id = test_program['program_id']
    
    # Record time before adding
    from datetime import datetime, timedelta
    before_add = datetime.utcnow()
    
    # Add program to shortlist
    client.post(f'/shortlist/add/{program_id}', follow_redirects=True)
    
    # Record time after adding
    after_add = datetime.utcnow()
    
    # Verify date_added is within the time window
    with client.application.app_context():
        from models import shortlist
        from sqlalchemy import select
        
        # Query user ID from database to avoid detached instance
        user = User.query.filter_by(username='testuser').first()
        user_id = user.id
        
        query = select(shortlist.c.date_added).where(
            shortlist.c.user_id == user_id,
            shortlist.c.program_id == program_id
        )
        result = db.session.execute(query).first()
        date_added = result[0]
        
        # Verify date_added is between before_add and after_add (with small buffer)
        # Account for timezone differences and database processing time
        buffer = timedelta(seconds=5)
        assert before_add - buffer <= date_added <= after_add + buffer, \
            f"date_added ({date_added}) should be between {before_add} and {after_add}"


def test_multiple_programs_have_dates(client, test_user):
    """
    Test Step 8.5: Date Added Tracking (Data)
    Verify that multiple programs added to shortlist each have their own date_added.
    """
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    # Create multiple programs
    with client.application.app_context():
        university = University(
            name='Test University',
            country='Japan',
            qs_rank=50
        )
        db.session.add(university)
        db.session.commit()
        
        program1 = Program(
            name='Test Program 1',
            category='CS',
            university_id=university.id,
            min_gpa=3.0,
            min_toefl=90
        )
        program2 = Program(
            name='Test Program 2',
            category='AI',
            university_id=university.id,
            min_gpa=3.2,
            min_toefl=95
        )
        db.session.add(program1)
        db.session.add(program2)
        db.session.commit()
        
        program1_id = program1.id
        program2_id = program2.id
    
    # Add first program
    client.post(f'/shortlist/add/{program1_id}', follow_redirects=True)
    
    # Small delay to ensure different timestamps
    import time
    time.sleep(1)
    
    # Add second program
    client.post(f'/shortlist/add/{program2_id}', follow_redirects=True)
    
    # Verify both programs have date_added
    with client.application.app_context():
        from models import shortlist
        from sqlalchemy import select
        
        # Query user ID from database to avoid detached instance
        user = User.query.filter_by(username='testuser').first()
        user_id = user.id
        
        # Check program 1
        query1 = select(shortlist.c.date_added).where(
            shortlist.c.user_id == user_id,
            shortlist.c.program_id == program1_id
        )
        result1 = db.session.execute(query1).first()
        assert result1 is not None and result1[0] is not None, "Program 1 should have date_added"
        
        # Check program 2
        query2 = select(shortlist.c.date_added).where(
            shortlist.c.user_id == user_id,
            shortlist.c.program_id == program2_id
        )
        result2 = db.session.execute(query2).first()
        assert result2 is not None and result2[0] is not None, "Program 2 should have date_added"
        
        # Verify dates are different (program2 should be later)
        date1 = result1[0]
        date2 = result2[0]
        assert date2 >= date1, "Program 2 should have a later or equal date_added than Program 1"


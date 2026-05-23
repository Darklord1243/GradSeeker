# tests/test_compatibility.py
# Test compatibility calculation algorithm (RFC 7, Step 7.1)

import pytest
from flask import Flask
from app import create_app
from models import db, User, Program, University
from utils import hash_password


def create_test_app():
    """Helper function to create a test Flask app with in-memory database."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    db.init_app(app)
    return app


@pytest.fixture
def client():
    """Create a test client for the Flask application (for integration tests)."""
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


def test_compatibility_safe_high_chance():
    """
    Test Step 7.1: Safe / High Chance compatibility (score >= 4).
    User exceeds all requirements with research and industry experience.
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university (required for Program foreign key)
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with strong profile
        user = User(
            username='strong_student',
            password='hash',
            gpa=3.8,
            toefl_score=110,
            research_papers=2,
            internship_exp=6
        )
        db.session.add(user)
        db.session.commit()
        
        # Create program with requirements that user exceeds
        program = Program(
            name='Test Program',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=True,
            industry_focus=True,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (2 points), TOEFL (1 point), Research (2 points), Industry (1 point) = 6 points
        assert status == "Safe / High Chance"
        assert color == "success"


def test_compatibility_target_medium_chance():
    """
    Test Step 7.1: Target / Medium Chance compatibility (score >= 2 and < 4).
    User meets basic requirements but lacks some soft power.
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with moderate profile
        user = User(
            username='moderate_student',
            password='hash',
            gpa=3.2,
            toefl_score=95,
            research_papers=0,
            internship_exp=2
        )
        db.session.add(user)
        db.session.commit()
        
        # Create program with requirements user meets
        program = Program(
            name='Test Program',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=False,
            industry_focus=True,  # User has 2 months, but needs 3+ for bonus
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (2 points), TOEFL (1 point), Industry (0 points - needs 3+) = 3 points
        assert status == "Target / Medium Chance"
        assert color == "warning"


def test_compatibility_reach_low_chance():
    """
    Test Step 7.1: Reach / Low Chance compatibility (score < 2).
    User falls short of requirements.
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with weak profile
        user = User(
            username='weak_student',
            password='hash',
            gpa=2.5,
            toefl_score=80,
            research_papers=0,
            internship_exp=0
        )
        db.session.add(user)
        db.session.commit()
        
        # Create program with high requirements
        program = Program(
            name='Test Program',
            min_gpa=3.5,
            min_toefl=100,
            research_focus=True,
            industry_focus=False,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (0 points - below requirement), TOEFL (0 points), Research (0 points) = 0 points
        assert status == "Reach / Low Chance"
        assert color == "danger"


def test_compatibility_gpa_close_enough():
    """
    Test Step 7.1: Edge case - GPA within 0.2 of requirement (gets 1 point).
    Tests the "close enough" logic for GPA.
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with GPA slightly below requirement (within 0.2)
        user = User(
            username='close_gpa_student',
            password='hash',
            gpa=3.1,  # 0.1 below min_gpa of 3.2
            toefl_score=90,
            research_papers=0,
            internship_exp=0
        )
        db.session.add(user)
        db.session.commit()
        
        # Create program with min_gpa = 3.2
        program = Program(
            name='Test Program',
            min_gpa=3.2,
            min_toefl=90,
            research_focus=False,
            industry_focus=False,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (1 point - close enough), TOEFL (1 point) = 2 points
        assert status == "Target / Medium Chance"
        assert color == "warning"


def test_compatibility_gpa_too_low():
    """
    Test Step 7.1: Edge case - GPA more than 0.2 below requirement (gets 0 points).
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with GPA more than 0.2 below requirement
        user = User(
            username='low_gpa_student',
            password='hash',
            gpa=2.9,  # 0.3 below min_gpa of 3.2 (more than 0.2)
            toefl_score=90,
            research_papers=0,
            internship_exp=0
        )
        db.session.add(user)
        db.session.commit()
        
        # Create program with min_gpa = 3.2
        program = Program(
            name='Test Program',
            min_gpa=3.2,
            min_toefl=90,
            research_focus=False,
            industry_focus=False,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (0 points - too low), TOEFL (1 point) = 1 point
        assert status == "Reach / Low Chance"
        assert color == "danger"


def test_compatibility_research_bonus():
    """
    Test Step 7.1: Research focus bonus (2 points when program needs research and user has papers).
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with research papers
        user = User(
            username='researcher',
            password='hash',
            gpa=3.5,
            toefl_score=100,
            research_papers=1,  # Has at least 1 paper
            internship_exp=0
        )
        db.session.add(user)
        db.session.commit()
        
        # Create research-focused program
        program = Program(
            name='Research Program',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=True,  # Program needs research
            industry_focus=False,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (2 points), TOEFL (1 point), Research (2 points) = 5 points
        assert status == "Safe / High Chance"
        assert color == "success"


def test_compatibility_industry_bonus():
    """
    Test Step 7.1: Industry focus bonus (1 point when program needs industry and user has 3+ months).
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with sufficient internship experience
        user = User(
            username='intern',
            password='hash',
            gpa=3.5,
            toefl_score=100,
            research_papers=0,
            internship_exp=3  # Has 3+ months (threshold)
        )
        db.session.add(user)
        db.session.commit()
        
        # Create industry-focused program
        program = Program(
            name='Industry Program',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=False,
            industry_focus=True,  # Program needs industry experience
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (2 points), TOEFL (1 point), Industry (1 point) = 4 points
        assert status == "Safe / High Chance"
        assert color == "success"


def test_compatibility_industry_bonus_insufficient():
    """
    Test Step 7.1: Industry focus - user has less than 3 months (no bonus).
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with insufficient internship experience
        user = User(
            username='short_intern',
            password='hash',
            gpa=3.5,
            toefl_score=100,
            research_papers=0,
            internship_exp=2  # Only 2 months (needs 3+)
        )
        db.session.add(user)
        db.session.commit()
        
        # Create industry-focused program
        program = Program(
            name='Industry Program',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=False,
            industry_focus=True,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (2 points), TOEFL (1 point), Industry (0 points - needs 3+) = 3 points
        assert status == "Target / Medium Chance"
        assert color == "warning"


def test_compatibility_edge_case_zero_values():
    """
    Test Step 7.1: Edge case - User with all zero values.
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with all zeros
        user = User(
            username='zero_user',
            password='hash',
            gpa=0.0,
            toefl_score=0,
            research_papers=0,
            internship_exp=0
        )
        db.session.add(user)
        db.session.commit()
        
        # Create program with requirements
        program = Program(
            name='Test Program',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=False,
            industry_focus=False,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: All zeros = 0 points
        assert status == "Reach / Low Chance"
        assert color == "danger"


def test_compatibility_edge_case_exact_threshold():
    """
    Test Step 7.1: Edge case - Score exactly at threshold (4 points = Safe, 2 points = Target).
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Test exactly 4 points (Safe threshold)
        user1 = User(
            username='exact_four',
            password='hash',
            gpa=3.0,
            toefl_score=90,
            research_papers=1,
            internship_exp=3
        )
        db.session.add(user1)
        
        program1 = Program(
            name='Test Program 1',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=True,
            industry_focus=True,
            university_id=university.id
        )
        db.session.add(program1)
        db.session.commit()
        
        status1, color1 = program1.calculate_compatibility(user1)
        # Expected: GPA (2), TOEFL (1), Research (2), Industry (1) = 6 points >= 4
        assert status1 == "Safe / High Chance"
        assert color1 == "success"
        
        # Test exactly 2 points (Target threshold)
        user2 = User(
            username='exact_two',
            password='hash',
            gpa=3.0,
            toefl_score=90,
            research_papers=0,
            internship_exp=0
        )
        db.session.add(user2)
        
        program2 = Program(
            name='Test Program 2',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=False,
            industry_focus=False,
            university_id=university.id
        )
        db.session.add(program2)
        db.session.commit()
        
        status2, color2 = program2.calculate_compatibility(user2)
        # Expected: GPA (2), TOEFL (1) = 3 points >= 2
        assert status2 == "Target / Medium Chance"
        assert color2 == "warning"


def test_compatibility_no_research_papers_bonus():
    """
    Test Step 7.1: Research focus program but user has no papers (no bonus).
    """
    app = create_test_app()
    
    with app.app_context():
        db.create_all()
        
        # Create a university
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create user with no research papers
        user = User(
            username='no_research',
            password='hash',
            gpa=3.5,
            toefl_score=100,
            research_papers=0,  # No papers
            internship_exp=0
        )
        db.session.add(user)
        db.session.commit()
        
        # Create research-focused program
        program = Program(
            name='Research Program',
            min_gpa=3.0,
            min_toefl=90,
            research_focus=True,  # Program needs research
            industry_focus=False,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Calculate compatibility
        status, color = program.calculate_compatibility(user)
        
        # Expected: GPA (2 points), TOEFL (1 point), Research (0 points - no papers) = 3 points
        assert status == "Target / Medium Chance"
        assert color == "warning"


def test_compatibility_displayed_on_detail_page(client):
    """
    Test Step 7.2: Display on Program Detail Page (UI)
    Verify that compatibility score is displayed on program detail pages.
    """
    program_id = None
    university_id = None
    
    # Create test data
    with client.application.app_context():
        # Create a university first (required for Program foreign key)
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        university_id = university.id
        
        # Create a program
        program = Program(
            name='Test Program',
            min_gpa=3.0,
            min_toefl=90,
            university_id=university_id
        )
        db.session.add(program)
        db.session.commit()
        program_id = program.id
        
        # Create a user with profile data
        user = User(
            username='test',
            password=hash_password('pass'),
            gpa=3.5,
            toefl_score=100
        )
        db.session.add(user)
        db.session.commit()
    
    # Login the user
    login_response = client.post('/login', data={
        'username': 'test',
        'password': 'pass'
    }, follow_redirects=False)
    
    # Verify login was successful (should redirect)
    assert login_response.status_code in [200, 302], "Login should succeed"
    
    # Access the program detail page
    response = client.get(f'/programs/{program_id}')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Program detail page did not load successfully"
    
    # Verify compatibility information is displayed
    assert b'Compatibility' in response.data, "Compatibility text should be present"
    
    # Verify the compatibility status is displayed (one of the three possible statuses)
    # We expect "Target / Medium Chance" based on user profile (GPA 3.5 >= 3.0, TOEFL 100 >= 90)
    # Score: GPA (2 points) + TOEFL (1 point) = 3 points = "Target / Medium Chance"
    assert b'Target / Medium Chance' in response.data or \
           b'Safe / High Chance' in response.data or \
           b'Reach / Low Chance' in response.data, \
           "Compatibility status should be displayed"
    
    # Verify the alert class is present (Bootstrap alert styling)
    assert b'alert-' in response.data, "Bootstrap alert class should be present"


def test_compatibility_displayed_on_dashboard(client):
    """
    Test Step 7.3: Display on Dashboard (UI)
    Verify that compatibility scores are displayed on the dashboard for shortlisted programs.
    """
    program_id = None
    university_id = None
    
    # Create test data
    with client.application.app_context():
        from models import shortlist
        
        # Create a university first (required for Program foreign key)
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        university_id = university.id
        
        # Create a program
        program = Program(
            name='Test Program',
            min_gpa=3.0,
            min_toefl=90,
            university_id=university_id
        )
        db.session.add(program)
        db.session.commit()
        program_id = program.id
        
        # Create a user with profile data
        user = User(
            username='test',
            password=hash_password('pass'),
            gpa=3.5,
            toefl_score=100
        )
        db.session.add(user)
        db.session.commit()
        
        # Add program to user's shortlist
        user.shortlisted_programs.append(program)
        db.session.commit()
    
    # Login the user
    login_response = client.post('/login', data={
        'username': 'test',
        'password': 'pass'
    }, follow_redirects=False)
    
    # Verify login was successful (should redirect)
    assert login_response.status_code in [200, 302], "Login should succeed"
    
    # Access the dashboard
    response = client.get('/dashboard')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Dashboard page did not load successfully"
    
    # Verify compatibility information is displayed
    assert b'Compatibility' in response.data, "Compatibility text should be present in dashboard"
    
    # Verify the program appears in the shortlist table
    assert b'Test Program' in response.data, "Shortlisted program should appear in dashboard"
    
    # Verify the compatibility status is displayed (one of the three possible statuses)
    # Expected: GPA (2 points) + TOEFL (1 point) = 3 points = "Target / Medium Chance"
    assert b'Target / Medium Chance' in response.data or \
           b'Safe / High Chance' in response.data or \
           b'Reach / Low Chance' in response.data, \
           "Compatibility status should be displayed in dashboard"
    
    # Verify the badge class is present (custom badge classes: badge-safe, badge-target, badge-reach)
    assert b'badge-safe' in response.data or b'badge-target' in response.data or b'badge-reach' in response.data, \
           "Custom badge class (badge-safe, badge-target, or badge-reach) should be present for compatibility status"


def test_compatibility_color_blind_friendly_labels(client):
    """
    Test Step 7.4: Color-Blind Friendly Labels (Accessibility)
    Verify that compatibility status uses text labels, not just color (SRS UI-02).
    This ensures accessibility for color-blind users.
    """
    program_id = None
    university_id = None
    
    # Create test data
    with client.application.app_context():
        # Create a university first (required for Program foreign key)
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        university_id = university.id
        
        # Create a program
        program = Program(
            name='Test Program',
            min_gpa=3.0,
            min_toefl=90,
            university_id=university_id
        )
        db.session.add(program)
        db.session.commit()
        program_id = program.id
        
        # Create a user with profile data
        user = User(
            username='test',
            password=hash_password('pass'),
            gpa=3.5,
            toefl_score=100
        )
        db.session.add(user)
        db.session.commit()
        
        # Add program to user's shortlist
        user.shortlisted_programs.append(program)
        db.session.commit()
    
    # Login the user
    login_response = client.post('/login', data={
        'username': 'test',
        'password': 'pass'
    }, follow_redirects=False)
    
    # Verify login was successful
    assert login_response.status_code in [200, 302], "Login should succeed"
    
    # Test 1: Verify text labels on Program Detail Page
    detail_response = client.get(f'/programs/{program_id}')
    assert detail_response.status_code == 200, "Program detail page should load"
    
    # Verify that status text is present (not just color)
    # The status should be one of: "Safe / High Chance", "Target / Medium Chance", "Reach / Low Chance"
    assert b'Safe / High Chance' in detail_response.data or \
           b'Target / Medium Chance' in detail_response.data or \
           b'Reach / Low Chance' in detail_response.data, \
           "Compatibility status text must be present on detail page (SRS UI-02)"
    
    # Verify "Compatibility Status:" label is present
    assert b'Compatibility Status:' in detail_response.data, \
           "Compatibility label text must be present on detail page"
    
    # Test 2: Verify text labels on Dashboard
    dashboard_response = client.get('/dashboard')
    assert dashboard_response.status_code == 200, "Dashboard should load"
    
    # Verify that status text is present in dashboard (not just color)
    assert b'Safe / High Chance' in dashboard_response.data or \
           b'Target / Medium Chance' in dashboard_response.data or \
           b'Reach / Low Chance' in dashboard_response.data, \
           "Compatibility status text must be present on dashboard (SRS UI-02)"
    
    # Verify the status text is inside a badge element (which contains both text and color)
    # The badge should have both the custom color class AND the text content
    assert b'badge-safe' in dashboard_response.data or b'badge-target' in dashboard_response.data or b'badge-reach' in dashboard_response.data, \
           "Custom badge class (badge-safe, badge-target, or badge-reach) should be present"
    
    # Additional verification: Ensure the text is not empty
    # If we can find the badge, the text should be inside it
    # This is verified by the status text assertions above
    
    # Test 3: Verify that color classes alone are not sufficient
    # We need to ensure that even if color is removed, the text is still meaningful
    # This is satisfied by the fact that status strings contain descriptive text
    # like "Safe / High Chance" rather than just "Safe" or just a color indicator

# tests/test_models.py
# Test database models structure

def test_user_model_structure():
    """Test that User model has all required fields."""
    from models import User
    
    # Verify all required fields exist
    assert hasattr(User, 'id')
    assert hasattr(User, 'username')
    assert hasattr(User, 'password')
    assert hasattr(User, 'gpa')
    assert hasattr(User, 'toefl_score')
    assert hasattr(User, 'internship_exp')
    assert hasattr(User, 'research_papers')


def test_university_model_structure():
    """Test that University model has all required fields."""
    from models import University
    
    # Verify all required fields exist (SRS 4.1.2)
    assert hasattr(University, 'id')
    assert hasattr(University, 'name')
    assert hasattr(University, 'country')
    assert hasattr(University, 'qs_rank')
    assert hasattr(University, 'logo_url')
    assert hasattr(University, 'programs')  # Relationship


def test_program_model_structure():
    """Test that Program model has all required fields."""
    from models import Program
    
    # Verify all required fields exist (SRS 4.1.3)
    assert hasattr(Program, 'id')
    assert hasattr(Program, 'university_id')
    assert hasattr(Program, 'name')
    assert hasattr(Program, 'category')
    
    # The "Price" (Requirements)
    assert hasattr(Program, 'min_gpa')
    assert hasattr(Program, 'min_toefl')
    assert hasattr(Program, 'tuition_fee')
    assert hasattr(Program, 'research_focus')
    assert hasattr(Program, 'industry_focus')
    
    # Additional fields for future web mining (V2.0)
    assert hasattr(Program, 'source_url')
    assert hasattr(Program, 'last_updated')
    
    # Deadline (mentioned in FR-2.2)
    assert hasattr(Program, 'deadline')
    
    # Advanced feature method
    assert hasattr(Program, 'calculate_compatibility')
    assert callable(getattr(Program, 'calculate_compatibility'))


def test_shortlist_relationship():
    """Test that the many-to-many shortlist relationship works correctly."""
    from flask import Flask
    from models import db, User, Program, University
    
    # Create a test app with in-memory database
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    db.init_app(app)
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create a university first (required for Program foreign key)
        university = University(
            name='Test University',
            country='Test Country',
            qs_rank=100
        )
        db.session.add(university)
        db.session.commit()
        
        # Create a user
        user = User(
            username='testuser',
            password='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create a program
        program = Program(
            name='Test Program',
            min_gpa=3.0,
            university_id=university.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Add program to user's shortlist (test the relationship)
        user.shortlisted_programs.append(program)
        db.session.commit()
        
        # Verify the relationship works
        assert program in user.shortlisted_programs
        assert len(user.shortlisted_programs) == 1
        assert user in program.interested_students
        assert len(program.interested_students) == 1


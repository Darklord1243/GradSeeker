# tests/test_load_data.py
# Tests for CSV data loading functionality

import os
import pytest
import sys

# Add parent directory to path to import load_data
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from load_data import read_csv_data, load_data_to_db
from app import create_app
from models import db, University, Program


def test_read_csv_exists():
    """Test that CSV file exists"""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(script_dir, 'universities.csv')
    assert os.path.exists(csv_path), f"CSV file not found at {csv_path}"


def test_read_csv():
    """Test that read_csv_data function reads CSV correctly"""
    data = read_csv_data('universities.csv')
    
    # Verify data is not empty
    assert len(data) >= 5, f"Expected at least 5 rows, got {len(data)}"
    
    # Verify first row has expected keys
    assert 'university_name' in data[0], "Missing 'university_name' key"
    assert 'program_name' in data[0], "Missing 'program_name' key"
    assert 'country' in data[0], "Missing 'country' key"
    assert 'min_gpa' in data[0], "Missing 'min_gpa' key"
    assert 'min_toefl' in data[0], "Missing 'min_toefl' key"
    assert 'research_focus' in data[0], "Missing 'research_focus' key"
    assert 'industry_focus' in data[0], "Missing 'industry_focus' key"


def test_read_csv_data_structure():
    """Test that CSV data has correct structure"""
    data = read_csv_data('universities.csv')
    
    # Verify it's a list
    assert isinstance(data, list), "Data should be a list"
    
    # Verify each row is a dictionary
    for row in data:
        assert isinstance(row, dict), "Each row should be a dictionary"
        
        # Verify required fields exist (even if empty)
        required_fields = [
            'university_name', 'country', 'program_name', 
            'min_gpa', 'min_toefl', 'research_focus', 'industry_focus'
        ]
        for field in required_fields:
            assert field in row, f"Missing required field: {field}"


def test_read_csv_file_not_found():
    """Test that function raises FileNotFoundError for non-existent file"""
    with pytest.raises(FileNotFoundError):
        read_csv_data('nonexistent_file.csv')


def test_read_csv_minimum_data():
    """Test that CSV has minimum required data (at least 5 universities/programs)"""
    data = read_csv_data('universities.csv')
    
    # Count unique universities
    universities = set(row['university_name'] for row in data)
    assert len(universities) >= 1, "Should have at least 1 university"
    
    # Verify total programs
    assert len(data) >= 5, f"Should have at least 5 programs, got {len(data)}"


# Integration Tests for Database Population

def test_load_data_to_database():
    """Test that load_data_to_db function populates database correctly"""
    # Create fresh test app with in-memory database (don't reuse create_app)
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Load data from CSV
        universities_created, programs_created = load_data_to_db(app, 'universities.csv')
        
        # Verify universities were created
        assert universities_created >= 1, f"Should have created at least 1 university, got {universities_created}"
        assert University.query.count() >= 1, "Database should have at least 1 university"
        
        # Verify programs were created
        assert programs_created >= 5, f"Should have created at least 5 programs, got {programs_created}"
        assert Program.query.count() >= 5, "Database should have at least 5 programs"


def test_load_data_duplicate_prevention():
    """Test that loading data twice doesn't create duplicates"""
    # Create fresh test app with in-memory database (don't reuse create_app)
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Load data first time
        universities_1, programs_1 = load_data_to_db(app, 'universities.csv')
        
        # Verify first load created data
        assert universities_1 > 0, f"First load should create universities, got {universities_1}"
        assert programs_1 > 0, f"First load should create programs, got {programs_1}"
        
        # Load data second time (should not create duplicates)
        universities_2, programs_2 = load_data_to_db(app, 'universities.csv')
        
        # Second load should not create new universities or programs
        assert universities_2 == 0, f"Second load should not create duplicate universities, got {universities_2}"
        assert programs_2 == 0, f"Second load should not create duplicate programs, got {programs_2}"
        
        # Verify counts match first load
        assert University.query.count() == universities_1, \
            f"University count should be {universities_1}, got {University.query.count()}"
        assert Program.query.count() == programs_1, \
            f"Program count should be {programs_1}, got {Program.query.count()}"


def test_load_data_hierarchical_structure():
    # Create fresh test app with in-memory database (don't reuse create_app)
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        load_data_to_db(app, 'universities.csv')
        
        # Step 2.5: Get distinct countries and verify structure
        # RFC 2, Step 2.5 - Verify Country → University → Program hierarchy
        countries = db.session.query(University.country).distinct().all()
        assert len(countries) >= 1, "Should have at least 1 country"
        
        # Verify each country has universities
        for country_tuple in countries:
            country = country_tuple[0]
            if country:  # Skip None countries (defensive coding)
                universities = University.query.filter_by(country=country).all()
                assert len(universities) > 0, \
                    f"Country {country} should have at least 1 university"
                
                # Verify each university has programs
                for university in universities:
                    assert len(university.programs) > 0, \
                        f"University {university.name} (in {country}) should have at least 1 program"


def test_load_data_program_relationships():
    """Test that programs are correctly linked to universities"""
    # Create fresh test app with in-memory database (don't reuse create_app)
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        load_data_to_db(app, 'universities.csv')
        
        # Get a program and verify it has a university
        program = Program.query.first()
        assert program is not None, "Should have at least one program"
        assert program.university_id is not None, "Program should have university_id"
        assert program.university is not None, "Program should have university relationship"
        assert program.university.name is not None, "University should have a name"


def test_load_data_data_types():
    """Test that data types are correctly parsed and stored"""
    # Create fresh test app with in-memory database (don't reuse create_app)
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        load_data_to_db(app, 'universities.csv')
        
        # Get a program and verify data types
        program = Program.query.first()
        assert program is not None, "Should have at least one program"
        
        # Verify min_gpa is float
        assert isinstance(program.min_gpa, (int, float)), "min_gpa should be numeric"
        assert program.min_gpa > 0, "min_gpa should be positive"
        
        # Verify min_toefl is integer
        assert isinstance(program.min_toefl, int), "min_toefl should be integer"
        assert program.min_toefl >= 0, "min_toefl should be non-negative"
        
        # Verify boolean fields
        assert isinstance(program.research_focus, bool), "research_focus should be boolean"
        assert isinstance(program.industry_focus, bool), "industry_focus should be boolean"
        
        # Verify university has correct types
        university = program.university
        assert isinstance(university.name, str), "University name should be string"
        if university.qs_rank is not None:
            assert isinstance(university.qs_rank, int), "QS rank should be integer"


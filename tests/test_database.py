# tests/test_database.py
# Test database creation

def test_database_creation():
    """Test that database can be created with all required tables."""
    from flask import Flask
    from models import db, User, University, Program
    
    # Create a test app with in-memory database
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    db.init_app(app)
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Get table names using inspect (SQLAlchemy 1.4+ compatible method)
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_names = sorted(inspector.get_table_names())
        
        # Verify all required tables exist (sorted for comparison)
        expected_tables = sorted(['user', 'university', 'program', 'shortlist'])
        assert table_names == expected_tables, \
            f"Expected tables {expected_tables}, but found {table_names}"


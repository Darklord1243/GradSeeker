# tests/test_app_init.py
# Test Flask application initialization

import os

def test_app_creates():
    """Test that the Flask app can be created and configured correctly."""
    from app import create_app
    app = create_app()
    assert app is not None
    
    # Check that database URI is set and points to instance/database.db
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    assert db_uri is not None
    assert 'sqlite:///' in db_uri
    assert 'database.db' in db_uri
    assert 'instance' in db_uri or os.path.join('instance', 'database.db') in db_uri


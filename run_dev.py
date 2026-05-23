from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Create database tables if they don't exist
    with app.app_context():
        from models import db
        db.create_all()
    
    # Run development server
    print("Starting Flask development server...")
    print("Open http://127.0.0.1:5000/register in your browser")
    app.run(debug=True, host='127.0.0.1', port=5000)

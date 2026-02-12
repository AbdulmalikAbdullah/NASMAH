# Database verification script

from app import create_app
from app.extensions import db
from app.models import User, TumorImage, Prediction, SystemLog, UserSession
from app.services.auth_service import AuthService


def verify_database():
    """Verify database setup and models"""
    app = create_app()
    
    with app.app_context():
        print("=== Database Verification ===\n")
        
        # Check if tables exist
        tables = db.inspect(db.engine).get_table_names()
        print(f"📋 Tables found: {', '.join(tables)}\n")
        
        expected_tables = ['users', 'tumor_images', 'predictions', 'system_logs', 'user_sessions']
        missing = [t for t in expected_tables if t not in tables]
        
        if missing:
            print(f"❌ Missing tables: {', '.join(missing)}")
            print("Run: python setup.py to initialize database")
            return False
        
        print("✅ All tables present\n")
        
        # Test creating a user
        try:
            # Check if test user exists
            test_user = User.query.filter_by(email='test@example.com').first()
            
            if not test_user:
                print("Creating test user...")
                test_user = AuthService.create_user(
                    fname='Test',
                    lname='User',
                    email='test@example.com',
                    password='TestPass123',
                    role='PATIENT'
                )
                print(f"✅ Test user created: {test_user.email}")
            else:
                print(f"✅ Test user already exists: {test_user.email}")
            
            # Query test
            users_count = User.query.count()
            print(f"📊 Total users in database: {users_count}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
        
        print("\n✨ Database verification complete!")
        return True


if __name__ == '__main__':
    verify_database()

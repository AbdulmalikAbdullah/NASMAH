# Quick setup script for the Flask backend

import os
import sys

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from .env.example")
            print("⚠️  Please update the .env file with your secret keys!")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")

def check_directories():
    """Ensure required directories exist"""
    dirs = ['uploads', 'models', 'instance']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("✅ Required directories verified")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")

def init_database():
    """Initialize the database"""
    print("\n🗄️  Initializing database...")
    from app import create_app
    from app.extensions import db
    
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully")

def main():
    """Run setup"""
    print("=== Lung Cancer AI Backend Setup ===\n")
    
    create_env_file()
    check_directories()
    
    response = input("\nInstall dependencies? (y/n): ")
    if response.lower() == 'y':
        install_dependencies()
    
    response = input("\nInitialize database? (y/n): ")
    if response.lower() == 'y':
        init_database()
    
    print("\n✨ Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your secret keys")
    print("2. Place your trained model in the models/ directory")
    print("3. Run: python run.py")

if __name__ == '__main__':
    main()

from app import create_app
from app.config import config
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variable or use default
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config[config_name])

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

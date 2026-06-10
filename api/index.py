import sys
import os

# Add root directory to sys.path so we can import 'backend' module and its contents
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import the Flask application instance
from backend.app import app

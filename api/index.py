import sys
import os

# Add root directory and backend directory to sys.path so we can import 'backend' and resolve local imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Import the Flask application instance
from backend.app import app

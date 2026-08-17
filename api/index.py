import sys
import os

# Add root directory and backend directories to sys.path so we can import 'backend' and resolve local imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend", "agents"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend", "agent_tools"))

# Import the Flask application instance
from backend.app import app

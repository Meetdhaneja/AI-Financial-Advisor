import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.app.main import app

# Vercel expects the app to be named 'app'
app = app
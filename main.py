"""Compatibility entrypoint for running the API from the repository root.

Preferred commands:
    uvicorn backend.main:app --port 8765
    cd backend && uvicorn main:app --port 8765
"""

from backend.main import app

"""
ExamFlow Main Application Runner
Executes the Flask development server on http://127.0.0.1:5000
"""

import sys
from app import app
from database import init_db

if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print(" ExamFlow: Examination Seating & Planning System")
    print(" Starting local development server...")
    print(" Access URL: http://127.0.0.1:5000")
    print(" Press CTRL+C to quit.")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)

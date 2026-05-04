"""
app.py — Entry point for PayrollPro.
Run this file to start the application:
    python app.py
"""

import sys
import os

# Make sure all modules are importable from this directory
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from login import run_login
from main import launch


def main():
    # 1. Initialise (or migrate) the SQLite database
    db.init_db()

    # 2. Show login window; returns user dict on success, None if closed
    user = run_login()
    if not user:
        print("Login cancelled — exiting.")
        return

    # 3. Launch the main application
    launch(user)


if __name__ == "__main__":
    main()

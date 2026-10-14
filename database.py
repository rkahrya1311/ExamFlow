"""
ExamFlow Database Management Module
Handles SQLite schema creation, connections, transactions, and data seeding.
"""

import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examflow.db")


def get_db_connection() -> sqlite3.Connection:
    """Return an active connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(force_recreate: bool = False):
    """Initialize database tables."""
    if force_recreate and os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER DEFAULT 3,
        email TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Classrooms table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classrooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        building TEXT DEFAULT 'Academic Block',
        floor INTEGER DEFAULT 1,
        rows INTEGER NOT NULL CHECK(rows > 0),
        columns INTEGER NOT NULL CHECK(columns > 0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Examinations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS examinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        exam_code TEXT UNIQUE NOT NULL,
        date TEXT NOT NULL,
        session_time TEXT NOT NULL,
        status TEXT DEFAULT 'DRAFT' CHECK(status IN ('DRAFT', 'ALLOCATED', 'FAILED')),
        allocation_notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Participating departments for an examination
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exam_departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL REFERENCES examinations(id) ON DELETE CASCADE,
        department TEXT NOT NULL,
        UNIQUE(exam_id, department)
    );
    """)

    # Participating classrooms for an examination
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exam_classrooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL REFERENCES examinations(id) ON DELETE CASCADE,
        classroom_id INTEGER NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
        UNIQUE(exam_id, classroom_id)
    );
    """)

    # High-level Room Allocations per Exam
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS room_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL REFERENCES examinations(id) ON DELETE CASCADE,
        classroom_id INTEGER NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
        dept_left TEXT NOT NULL,
        dept_right TEXT NOT NULL,
        benches_used INTEGER NOT NULL CHECK(benches_used > 0),
        students_left_count INTEGER NOT NULL,
        students_right_count INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(exam_id, classroom_id)
    );
    """)

    # Exact bench seating assignment
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seating_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL REFERENCES examinations(id) ON DELETE CASCADE,
        classroom_id INTEGER NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        row_num INTEGER NOT NULL,
        col_num INTEGER NOT NULL,
        bench_num INTEGER NOT NULL,
        seat_position TEXT NOT NULL CHECK(seat_position IN ('LEFT', 'RIGHT')),
        department TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(exam_id, classroom_id, bench_num, seat_position),
        UNIQUE(exam_id, student_id)
    );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database schema successfully initialized.")

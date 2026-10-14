"""
ExamFlow Sample Data Generator
Populates test databases and exports CSV templates for immediate demonstration.
Includes customized 6 rows x 5 columns hall configuration for AI&DS-B and CSE-B.
"""

import os
import csv
from database import get_db_connection, init_db


def generate_sample_csvs(output_dir: str = "."):
    """Creates sample CSV files for testing upload functionality."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Custom AI&DS-B and CSE-B Dataset (30 AI&DS-B, 30 CSE-B = 60 Students for 6x5 hall)
    aids_cse_path = os.path.join(output_dir, "sample_aids_b_cse_b.csv")
    with open(aids_cse_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["roll_number", "name", "department", "year", "email"])
        for i in range(1, 31):
            writer.writerow([f"23AD-B{i:02d}", f"AI&DS-B Student {i}", "AI&DS-B", 3, f"aids_b{i:02d}@college.edu"])
        for i in range(1, 31):
            writer.writerow([f"23CS-B{i:02d}", f"CSE-B Student {i}", "CSE-B", 3, f"cse_b{i:02d}@college.edu"])

    # 2. General Valid Balanced Dataset (40 CSE, 30 ECE, 10 MECH = 80 Students)
    valid_path = os.path.join(output_dir, "sample_students_valid.csv")
    with open(valid_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["roll_number", "name", "department", "year", "email"])
        for i in range(1, 41):
            writer.writerow([f"23CS{i:03d}", f"CSE Student {i}", "CSE", 3, f"cs{i:03d}@college.edu"])
        for i in range(1, 31):
            writer.writerow([f"23EC{i:03d}", f"ECE Student {i}", "ECE", 3, f"ec{i:03d}@college.edu"])
        for i in range(1, 11):
            writer.writerow([f"23ME{i:03d}", f"MECH Student {i}", "MECH", 3, f"me{i:03d}@college.edu"])

    # 3. Incompatible (>50% single department) Dataset
    incomp_path = os.path.join(output_dir, "sample_students_incompatible.csv")
    with open(incomp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["roll_number", "name", "department", "year", "email"])
        for i in range(1, 46):
            writer.writerow([f"23CS{i:03d}", f"CSE Student {i}", "CSE", 3, f"cs{i:03d}@college.edu"])
        for i in range(1, 11):
            writer.writerow([f"23EC{i:03d}", f"ECE Student {i}", "ECE", 3, f"ec{i:03d}@college.edu"])

    # 4. Odd Total Dataset (Violates 2-per-bench parity)
    odd_path = os.path.join(output_dir, "sample_students_odd.csv")
    with open(odd_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["roll_number", "name", "department", "year", "email"])
        for i in range(1, 16):
            writer.writerow([f"23CS{i:03d}", f"CSE Student {i}", "CSE", 3, f"cs{i:03d}@college.edu"])
        for i in range(1, 15):
            writer.writerow([f"23EC{i:03d}", f"ECE Student {i}", "ECE", 3, f"ec{i:03d}@college.edu"])


def seed_database():
    """
    Populates database with:
    - Hall-605: 6 benches (rows) x 5 columns (30 benches = 60 seats)
    - LH-101, LH-102, LH-201
    - 30 Students of AI&DS-B and 30 Students of CSE-B
    - Pre-configured examination linking AI&DS-B and CSE-B to Hall-605
    """
    init_db(force_recreate=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Seed Classrooms - Including user's exact 6 benches x 5 columns hall!
    classrooms = [
        ("Hall-605", "Tech Complex", 2, 6, 5),  # 6 rows x 5 columns = 30 benches (60 seats)
        ("LH-101", "Science Block", 1, 5, 4),   # 5 rows x 4 columns = 20 benches (40 seats)
        ("LH-102", "Science Block", 1, 5, 3),   # 5 rows x 3 columns = 15 benches (30 seats)
        ("LH-201", "Engineering Block", 2, 4, 4), # 4 rows x 4 columns = 16 benches (32 seats)
    ]
    cursor.executemany("""
    INSERT INTO classrooms (room_number, building, floor, rows, columns)
    VALUES (?, ?, ?, ?, ?)
    """, classrooms)

    hall_605_id = cursor.execute("SELECT id FROM classrooms WHERE room_number = 'Hall-605'").fetchone()["id"]

    # Seed Students: 30 AI&DS-B and 30 CSE-B students (Total 60 for the 6x5 hall)
    students = []
    for i in range(1, 31):
        students.append((f"23AD-B{i:02d}", f"AI&DS-B Student {i}", "AI&DS-B", 3, f"aids_b{i:02d}@college.edu"))
    for i in range(1, 31):
        students.append((f"23CS-B{i:02d}", f"CSE-B Student {i}", "CSE-B", 3, f"cse_b{i:02d}@college.edu"))

    cursor.executemany("""
    INSERT INTO students (roll_number, name, department, year, email)
    VALUES (?, ?, ?, ?, ?)
    """, students)

    # Seed Examination: AI&DS-B & CSE-B Mid-Term in Hall-605 (6x5 grid)
    cursor.execute("""
    INSERT INTO examinations (title, exam_code, date, session_time, status, allocation_notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "Semester Examination: AI&DS-B & CSE-B",
        "EXAM-2026-AD-CS-B",
        "2026-10-25",
        "09:30 AM - 12:30 PM (FN)",
        "DRAFT",
        "Hall arrangement for 6 rows x 5 columns (30 benches = 60 seats) for AI&DS-B and CSE-B"
    ))

    exam_id = cursor.lastrowid

    # Register departments
    cursor.execute("INSERT INTO exam_departments (exam_id, department) VALUES (?, ?)", (exam_id, "AI&DS-B"))
    cursor.execute("INSERT INTO exam_departments (exam_id, department) VALUES (?, ?)", (exam_id, "CSE-B"))

    # Register Hall-605 for this exam
    cursor.execute("INSERT INTO exam_classrooms (exam_id, classroom_id) VALUES (?, ?)", (exam_id, hall_605_id))

    conn.commit()
    conn.close()
    generate_sample_csvs()
    print("Database seeded with Hall-605 (6x5 benches), 30 AI&DS-B students, and 30 CSE-B students.")


if __name__ == "__main__":
    seed_database()

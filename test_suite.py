"""
ExamFlow Automated Test Suite
Built with standard library unittest.
Verifies compliance with all Real College Examination Rules and Flask Web Application Routes.
"""

import unittest
import io
import os
import sys

# Ensure current directory is on python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database import init_db, get_db_connection
from allocator import pre_validate_exam, generate_seating_allocation, solve_classroom_pairings
from app import app
from sample_data import seed_database, generate_sample_csvs


class TestCollegeAllocationRules(unittest.TestCase):
    """Rigorous verification of Real College Rules in allocator.py"""

    def test_01_odd_student_parity_rejected(self):
        """Rule: Every occupied bench has 2 students -> total count MUST be even."""
        dept_counts = {"CSE": 21, "ECE": 20}  # 41 students
        caps = [30]
        valid, msg, audit = pre_validate_exam(dept_counts, caps)
        self.assertFalse(valid)
        self.assertIn("ODD", msg)

    def test_02_majority_exceeded_rejected(self):
        """Rule: No department can exceed 50% of total students across multiple departments."""
        dept_counts = {"CSE": 35, "ECE": 10, "MECH": 5}  # Total 50, CSE is 35 (70%), ECE+MECH is 15
        caps = [30, 30]
        valid, msg, audit = pre_validate_exam(dept_counts, caps)
        self.assertFalse(valid)
        self.assertIn("exceeds", msg.lower())

    def test_03_insufficient_classroom_capacity_rejected(self):
        """Rule: Bench capacity must be >= required benches."""
        dept_counts = {"CSE": 20, "ECE": 20}  # 40 students = 20 benches
        caps = [15]  # Only 15 benches
        valid, msg, audit = pre_validate_exam(dept_counts, caps)
        self.assertFalse(valid)
        self.assertIn("capacity", msg.lower())

    def test_04_single_department_rejected(self):
        """Rule: Exactly two distinct departments per classroom -> requires >= 2 depts."""
        dept_counts = {"CSE": 20}
        caps = [20]
        valid, msg, audit = pre_validate_exam(dept_counts, caps)
        self.assertFalse(valid)
        self.assertIn("departments", msg.lower())

    def test_05_two_departments_unequal_counts_rejected(self):
        """Rule: With exactly 2 departments, counts must be identical."""
        dept_counts = {"CSE": 20, "ECE": 18}
        caps = [30]
        valid, msg, audit = pre_validate_exam(dept_counts, caps)
        self.assertFalse(valid)
        self.assertIn("unequal", msg.lower())

    def test_06_valid_two_departments_allocation(self):
        """Rule: 2 departments paired with fixed left/right orientation."""
        students = {
            "CSE": [{"id": i, "name": f"CSE {i}", "roll_number": f"CS{i:03d}", "department": "CSE"} for i in range(1, 21)],
            "ECE": [{"id": 100 + i, "name": f"ECE {i}", "roll_number": f"EC{i:03d}", "department": "ECE"} for i in range(1, 21)]
        }
        classrooms = [
            {"id": 1, "room_number": "LH-101", "rows": 5, "columns": 4}  # 20 benches, 40 seats
        ]

        res = generate_seating_allocation(students, classrooms)
        self.assertTrue(res["success"])
        self.assertEqual(len(res["seating_assignments"]), 40)

        # Verify room allocation
        ra = res["room_allocations"][0]
        self.assertEqual(ra["dept_left"], "CSE")
        self.assertEqual(ra["dept_right"], "ECE")
        self.assertNotEqual(ra["dept_left"], ra["dept_right"])

        # Verify benches
        benches = {}
        for s in res["seating_assignments"]:
            benches.setdefault(s["bench_num"], []).append(s)

        self.assertEqual(len(benches), 20)
        for b_num, seats in benches.items():
            self.assertEqual(len(seats), 2)
            left_s = [s for s in seats if s["seat_position"] == "LEFT"][0]
            right_s = [s for s in seats if s["seat_position"] == "RIGHT"][0]
            self.assertEqual(left_s["department"], "CSE")
            self.assertEqual(right_s["department"], "ECE")

    def test_07_three_departments_multi_classroom_allocation(self):
        """Rule: 3 departments: CSE: 30, ECE: 20, MECH: 10 across 2 classrooms."""
        students = {
            "CSE": [{"id": i, "name": f"CSE {i}", "roll_number": f"CS{i:03d}", "department": "CSE"} for i in range(1, 31)],
            "ECE": [{"id": 100 + i, "name": f"ECE {i}", "roll_number": f"EC{i:03d}", "department": "ECE"} for i in range(1, 21)],
            "MECH": [{"id": 200 + i, "name": f"ME {i}", "roll_number": f"ME{i:03d}", "department": "MECH"} for i in range(1, 11)]
        }
        classrooms = [
            {"id": 1, "room_number": "LH-101", "rows": 5, "columns": 4},  # 20 benches
            {"id": 2, "room_number": "LH-102", "rows": 5, "columns": 3}   # 15 benches
        ]

        res = generate_seating_allocation(students, classrooms)
        self.assertTrue(res["success"])
        self.assertEqual(len(res["seating_assignments"]), 60)

        # Check: exactly 2 departments in every used classroom, no third dept
        for ra in res["room_allocations"]:
            c_id = ra["classroom_id"]
            room_seats = [s for s in res["seating_assignments"] if s["classroom_id"] == c_id]
            depts_in_room = set(s["department"] for s in room_seats)
            self.assertEqual(len(depts_in_room), 2, f"Room {ra['room_number']} must have exactly 2 departments")

        # Check: zero omission, zero duplicates
        assigned_ids = [s["student_id"] for s in res["seating_assignments"]]
        self.assertEqual(len(assigned_ids), 60)
        self.assertEqual(len(set(assigned_ids)), 60)

    def test_08_empty_benches_handled_validly(self):
        """Rule: Empty benches are permitted if remaining rules are satisfied."""
        students = {
            "CSE": [{"id": i, "name": f"CSE {i}", "roll_number": f"CS{i:03d}", "department": "CSE"} for i in range(1, 11)],
            "ECE": [{"id": 50 + i, "name": f"ECE {i}", "roll_number": f"EC{i:03d}", "department": "ECE"} for i in range(1, 11)]
        }
        classrooms = [
            {"id": 1, "room_number": "LH-BIG", "rows": 5, "columns": 5}  # 25 benches
        ]

        res = generate_seating_allocation(students, classrooms)
        self.assertTrue(res["success"])
        ra = res["room_allocations"][0]
        self.assertEqual(ra["benches_used"], 10)
        self.assertEqual(ra["empty_benches"], 15)
        self.assertEqual(len(res["seating_assignments"]), 20)


class TestWebRoutesAndIntegration(unittest.TestCase):
    """Integration tests for web routes, uploads, and PDF export."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        seed_database()

    def test_09_dashboard_renders(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"ExamFlow", resp.data)
        self.assertIn(b"Registered Students", resp.data)

    def test_10_students_page_renders(self):
        resp = self.client.get("/students")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Student Directory", resp.data)

    def test_11_csv_upload_valid(self):
        csv_data = "roll_number,name,department,year,email\n99CS01,Test CS,CSE,3,test@edu.com\n99EC01,Test EC,ECE,3,ec@edu.com\n"
        data = {
            "csv_file": (io.BytesIO(csv_data.encode("utf-8")), "test.csv")
        }
        resp = self.client.post("/students/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Successfully imported", resp.data)

    def test_12_classroom_add_flow(self):
        resp = self.client.post("/classrooms/add", data={
            "room_number": "ROOM-UNITTEST-1",
            "building": "Test Block",
            "floor": "2",
            "rows": "4",
            "columns": "4"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"ROOM-UNITTEST-1", resp.data)

    def test_13_allocation_execution_and_master_pdf(self):
        # Exam id 1 is seeded
        alloc_resp = self.client.post("/examinations/1/allocate", follow_redirects=True)
        self.assertEqual(alloc_resp.status_code, 200)
        self.assertIn(b"VERIFIED", alloc_resp.data)

        # Download master PDF
        pdf_resp = self.client.get("/examinations/1/pdf")
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp.mimetype, "application/pdf")
        self.assertGreater(len(pdf_resp.data), 1000)

    def test_14_door_notice_pdf(self):
        # Download door notice for room 1 of allocated exam
        self.client.post("/examinations/1/allocate", follow_redirects=True)
        notice_resp = self.client.get("/examinations/1/door-notice/1")
        self.assertEqual(notice_resp.status_code, 200)
        self.assertEqual(notice_resp.mimetype, "application/pdf")
        self.assertGreater(len(notice_resp.data), 500)


if __name__ == "__main__":
    unittest.main(verbosity=2)

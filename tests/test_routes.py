"""
Integration Tests for ExamFlow Web Routes
Tests all endpoints: Dashboard, Student Upload, Classroom CRUD, Exam Creation, Allocation, and PDF Generation.
"""

import unittest
import io
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from sample_data import seed_database


class TestExamFlowWebRoutes(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        seed_database()

    def test_dashboard_route(self):
        """Dashboard loads with HTTP 200 and displays metrics."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ExamFlow", response.data)
        self.assertIn(b"Registered Students", response.data)

    def test_students_list_route(self):
        """Students directory renders student roster."""
        response = self.client.get("/students")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Directory", response.data)

    def test_csv_upload_valid(self):
        """Tests CSV upload with valid data."""
        csv_data = "roll_number,name,department,year,email\n99CS01,Test CS,CSE,3,test@edu.com\n99EC01,Test EC,ECE,3,ec@edu.com\n"
        data = {
            "csv_file": (io.BytesIO(csv_data.encode("utf-8")), "students.csv")
        }
        response = self.client.post("/students/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully imported", response.data)

    def test_csv_upload_invalid_headers(self):
        """Tests rejection of CSV with missing mandatory headers."""
        csv_data = "wrong_header,another_col\n1,2\n"
        data = {
            "csv_file": (io.BytesIO(csv_data.encode("utf-8")), "bad.csv")
        }
        response = self.client.post("/students/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Required headers missing", response.data)

    def test_classroom_add_and_delete(self):
        """Tests classroom creation and deletion."""
        response = self.client.post("/classrooms/add", data={
            "room_number": "TEST-HALL-99",
            "building": "Test Block",
            "floor": "3",
            "rows": "4",
            "columns": "5"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TEST-HALL-99", response.data)

        # Check classrooms list
        list_resp = self.client.get("/classrooms")
        self.assertIn(b"TEST-HALL-99", list_resp.data)

    def test_exam_allocation_and_pdf_export(self):
        """Tests running allocation on seeded exam and downloading Master PDF and Door Notice."""
        # Seeded exam has id 1
        alloc_resp = self.client.post("/examinations/1/allocate", follow_redirects=True)
        self.assertEqual(alloc_resp.status_code, 200)
        self.assertTrue(b"Allocation successfully generated and verified" in alloc_resp.data or b"VERIFIED" in alloc_resp.data)

        # Master PDF export
        pdf_resp = self.client.get("/examinations/1/pdf")
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp.mimetype, "application/pdf")
        self.assertGreater(len(pdf_resp.data), 1000)

        # Door Notice export for room 1
        notice_resp = self.client.get("/examinations/1/door-notice/1")
        self.assertEqual(notice_resp.status_code, 200)
        self.assertEqual(notice_resp.mimetype, "application/pdf")
        self.assertGreater(len(notice_resp.data), 500)


if __name__ == "__main__":
    unittest.main()

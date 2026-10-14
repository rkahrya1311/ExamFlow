# Testing Documentation & Verification Report

This document records the automated testing strategy, executed test cases, and actual test results for ExamFlow.

---

## 1. Test Environment Specification

- **Operating System:** Windows 11 Enterprise (x64)
- **Python Version:** Python 3.11.9
- **Frameworks:** `unittest` (Standard Library) / `pytest 9.1.1`
- **Application Server:** Flask 3.1.3
- **Database:** SQLite 3 (WAL mode enabled)
- **PDF Engine:** ReportLab 5.0.1
- **Test File:** `test_suite.py` / `tests/test_allocator.py` / `tests/test_routes.py`

---

## 2. Test Execution Summary

```
----------------------------------------------------------------------
Ran 14 tests in 0.607s

OK (All 14 Passed, 0 Failures, 0 Errors, 0 Skipped)
```

---

## 3. Test Cases & Actual Results Matrix

| Test ID | Test Category | Target Function / Route | Input Parameters / Scenario | Expected Outcome | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Rule Verification | `pre_validate_exam` | Depts: `{"CSE": 21, "ECE": 20}` (Total 41, Odd) | Flagged as invalid due to odd count parity | Detected: "Total student count is 41 (ODD)" | **PASSED** |
| **TC-02** | Rule Verification | `pre_validate_exam` | Depts: `{"CSE": 35, "ECE": 10, "MECH": 5}` (CSE is 70%) | Flagged as invalid; exceeds 50% threshold | Detected: "Department 'CSE' has 35 students, which exceeds..." | **PASSED** |
| **TC-03** | Rule Verification | `pre_validate_exam` | Depts: `{"CSE": 20, "ECE": 20}`, Caps: `[15]` benches | Flagged as invalid due to capacity shortage | Detected: "Insufficient classroom capacity: 40 students require 20 benches..." | **PASSED** |
| **TC-04** | Rule Verification | `pre_validate_exam` | Depts: `{"CSE": 20}` (Only 1 department) | Flagged as invalid; requires $\ge 2$ departments | Detected: "Insufficient departments: Exactly 2 distinct departments are required..." | **PASSED** |
| **TC-05** | Rule Verification | `pre_validate_exam` | Depts: `{"CSE": 20, "ECE": 18}` (Unequal 2 depts) | Flagged as invalid; 2 depts must have equal counts | Detected: "Unequal department counts: With only 2 departments participating..." | **PASSED** |
| **TC-06** | Allocation Engine | `generate_seating_allocation` | 20 CSE, 20 ECE students; Room LH-101 (20 benches) | Exact allocation: Left=CSE, Right=ECE, 20 benches occupied | Verified: 40 seats allocated, zero violations | **PASSED** |
| **TC-07** | Allocation Engine | `generate_seating_allocation` | 30 CSE, 20 ECE, 10 MECH; Rooms LH-101 (20b), LH-102 (15b) | Partition across 2 rooms: Room 1 (CSE/ECE), Room 2 (CSE/MECH) | Verified: 60 students seated, zero duplicates, no 3rd dept in any room | **PASSED** |
| **TC-08** | Allocation Engine | `generate_seating_allocation` | 10 CSE, 10 ECE; Room LH-BIG (25 benches) | 10 benches occupied by pairs, 15 benches marked empty | Verified: 20 seats allocated, 15 empty benches recorded | **PASSED** |
| **TC-09** | Web Route | `GET /` | Client requests dashboard | HTTP 200; contains "ExamFlow" and summary stats | HTTP 200 OK | **PASSED** |
| **TC-10** | Web Route | `GET /students` | Client requests student directory | HTTP 200; contains "Student Directory" | HTTP 200 OK | **PASSED** |
| **TC-11** | Web Route | `POST /students/upload` | Valid CSV multipart upload (2 rows) | HTTP 200 redirect; "Successfully imported" flash | HTTP 200 OK; Flash confirmed | **PASSED** |
| **TC-12** | Web Route | `POST /classrooms/add` | Room: `ROOM-UNITTEST-1`, 4 rows $\times$ 4 cols | HTTP 200 redirect; Room listed with 16 benches | HTTP 200 OK; Room created | **PASSED** |
| **TC-13** | Web Route | `POST /examinations/1/allocate` & `GET /examinations/1/pdf` | Run allocation on exam 1, then download Master PDF | HTTP 200; Status=ALLOCATED; PDF binary $> 1000$ bytes | HTTP 200 OK; PDF bytes returned ($> 8$ KB) | **PASSED** |
| **TC-14** | Web Route | `GET /examinations/1/door-notice/1` | Download Door Notice PDF for Room 1 | HTTP 200; Content-Type: `application/pdf`; $> 500$ bytes | HTTP 200 OK; Door notice PDF returned | **PASSED** |

---

## 4. Test Execution Trace (Verifiable Output)

```
$ python test_suite.py
test_01_odd_student_parity_rejected (__main__.TestCollegeAllocationRules.test_01_odd_student_parity_rejected)
Rule: Every occupied bench has 2 students -> total count MUST be even. ... ok
test_02_majority_exceeded_rejected (__main__.TestCollegeAllocationRules.test_02_majority_exceeded_rejected)
Rule: No department can exceed 50% of total students across multiple departments. ... ok
test_03_insufficient_classroom_capacity_rejected (__main__.TestCollegeAllocationRules.test_03_insufficient_classroom_capacity_rejected)
Rule: Bench capacity must be >= required benches. ... ok
test_04_single_department_rejected (__main__.TestCollegeAllocationRules.test_04_single_department_rejected)
Rule: Exactly two distinct departments per classroom -> requires >= 2 depts. ... ok
test_05_two_departments_unequal_counts_rejected (__main__.TestCollegeAllocationRules.test_05_two_departments_unequal_counts_rejected)
Rule: With exactly 2 departments, counts must be identical. ... ok
test_06_valid_two_departments_allocation (__main__.TestCollegeAllocationRules.test_06_valid_two_departments_allocation)
Rule: 2 departments paired with fixed left/right orientation. ... ok
test_07_three_departments_multi_classroom_allocation (__main__.TestCollegeAllocationRules.test_07_three_departments_multi_classroom_allocation)
Rule: 3 departments: CSE: 30, ECE: 20, MECH: 10 across 2 classrooms. ... ok
test_08_empty_benches_handled_validly (__main__.TestCollegeAllocationRules.test_08_empty_benches_handled_validly)
Rule: Empty benches are permitted if remaining rules are satisfied. ... ok
test_09_dashboard_renders (__main__.TestWebRoutesAndIntegration.test_09_dashboard_renders) ... ok
test_10_students_page_renders (__main__.TestWebRoutesAndIntegration.test_10_students_page_renders) ... ok
test_11_csv_upload_valid (__main__.TestWebRoutesAndIntegration.test_11_csv_upload_valid) ... ok
test_12_classroom_add_flow (__main__.TestWebRoutesAndIntegration.test_12_classroom_add_flow) ... ok
test_13_allocation_execution_and_master_pdf (__main__.TestWebRoutesAndIntegration.test_13_allocation_execution_and_master_pdf) ... ok
test_14_door_notice_pdf (__main__.TestWebRoutesAndIntegration.test_14_door_notice_pdf) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.607s

OK
```

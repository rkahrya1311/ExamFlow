# Software Requirements Specification (SRS)

**Standard:** IEEE 830-1998 Recommended Practice for Software Requirements Specifications (Adapted)  
**System Name:** ExamFlow Examination Seating Allocation System  

---

## 1. Introduction

### 1.1 Purpose
This document provides the formal software requirements specification for ExamFlow, specifying functional and non-functional requirements, constraints, and interface specifications for the minimum viable product (MVP).

### 1.2 Intended Audience
Examination cell officers, chief invigilators, academic administrators, software engineers, and academic evaluators.

---

## 2. Functional Requirements (FR)

| Req ID | Requirement Title | Description | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **FR-01** | **Dashboard Metrics** | System must display active summaries of registered students, department cohorts, classroom capacities, and examination schedules. | Real-time counts render on load; quick action shortcuts function properly. |
| **FR-02** | **Student CSV Ingestion** | System must accept student roster CSV files with fields `roll_number`, `name`, `department`, `year`, `email`. | Validates headers; informs user of rows imported or rejected; prevents duplicate roll numbers. |
| **FR-03** | **Classroom Management** | System must allow administrators to define classrooms with room number, building, floor, rows, and columns. | Capacity is computed dynamically as $Rows \times Columns \times 2$; records persist in SQLite. |
| **FR-04** | **Examination Creation** | System must enable scheduling an exam with Title, Code, Date, Session, and participating departments. | Requires selection of at least 2 participating departments. |
| **FR-05** | **Pre-Allocation Audit** | System must mathematically verify inputs before executing allocation. | Rejects odd total count, single-department majority > 50%, unequal counts in 2-department exams, and capacity deficiencies. |
| **FR-06** | **Seating Allocation Solver** | System must execute a backtracking constraint satisfaction algorithm assigning pairs to rooms. | Each room has exactly 2 distinct departments; Left/Right orientation is fixed; bench holds 1 Left and 1 Right student. |
| **FR-07** | **Interactive Grid Visualizer** | System must render a 2D seating canvas showing teacher's podium, benches, row/column coords, roll numbers, names, and empty benches. | Room tabs switch views; empty benches explicitly labeled. |
| **FR-08** | **PDF Report Generation** | System must generate printable PDF documents for Master Seating Plan and Hall Door Notices. | PDFs contain table structures, invigilator signature boxes, and roll number ranges. |

---

## 3. Non-Functional Requirements (NFR)

### 3.1 Performance (NFR-01)
- The seating allocation algorithm shall compute valid seating arrangements for up to 1,000 students across 30 classrooms in less than 2.0 seconds.
- Web pages shall render within 200 ms under standard local development environments.

### 3.2 Correctness & Integrity (NFR-02)
- Zero False Positives: The system shall **never** report success for an invalid allocation.
- Completeness: Every participating student shall be allocated exactly one physical seat without omission or duplication.

### 3.3 Usability & Aesthetics (NFR-03)
- The interface shall implement a clean design system utilizing modern typography, responsive layout containers, distinct status badges, and contrasting color badges for Left and Right departments.
- Informative error banners shall provide clear mathematical explanations of why an allocation is impossible.

### 3.4 Reliability & Portability (NFR-04)
- The application shall run locally on standard Windows, Linux, and macOS systems with Python 3.10+ without requiring container virtualization or cloud network calls.
- SQLite transactions shall ensure that partial allocations are rolled back upon calculation failure.

### 3.5 Maintainability & Testability (NFR-05)
- Code shall maintain separation of concerns: database operations (`database.py`), mathematical engine (`allocator.py`), PDF rendering (`pdf_generator.py`), and HTTP endpoints (`app.py`).
- Automated tests shall be executable with standard test runners (`pytest` / `unittest`).

# Project Overview

**Project Title:** ExamFlow: A Web-Based Examination Seating Allocation and Classroom Planning System  
**Academic Level:** Bachelor of Technology / Computer Science and Engineering  
**Application Architecture:** Lightweight Monolithic Web Application (Flask, SQLite, Vanilla CSS/JS, ReportLab)

---

## 1. Executive Summary
Examination administration in universities and collegiate institutions is a recurring logistical challenge fraught with administrative friction. Among the most critical responsibilities of examination cells is the generation of invigilation seating arrangements. To prevent academic malpractice such as unauthorized communication and copying, institutions enforce rigorous physical segregation rules—primarily that adjacent students on any bench must belong to distinct academic departments.

**ExamFlow** is an open-source, automated examination seating allocation and classroom planning system. Built on a lightweight, dependable Python/Flask and SQLite stack, ExamFlow replaces manual spreadsheet drafting with a mathematically sound, constraint-satisfaction seating allocation engine.

---

## 2. Motivation
In most colleges, exam cells manually plan seating charts across dozens of halls:
- Manual planning consumes tens of man-hours per examination cycle.
- Human error frequently introduces subtle violations: two students from the same department seated on the same bench, unequal left/right department orientations across rows causing invigilation confusion, or capacity oversubscription.
- Sudden attendance list changes or uneven department cohort sizes require hours of manual recalculation.
- Generating physical door notices and master superintendent sheets requires manual data formatting and copy-pasting into word processors.

ExamFlow addresses these bottlenecks by providing instantaneous, rule-compliant allocation generation, pre-flight mathematical feasibility auditing, interactive bench grid visualization, and automated PDF export.

---

## 3. Scope of the System

### In-Scope (Completed Features in MVP):
1. **Interactive Examination Dashboard:** Real-time visibility into student counts, available classrooms, total bench capacities, and scheduled examinations.
2. **Student Roster Management:** Bulk CSV ingestion, schema validation, duplicate detection, cohort filtering, and template downloads (valid, odd count, and incompatible cohorts).
3. **Classroom Layout Configuration:** Multi-block, multi-floor classroom directory with customizable bench grid dimensions ($Rows \times Columns$), dynamic capacity calculation ($Rows \times Columns \times 2$), and bench-level layout tracking.
4. **Examination Scheduling:** Exam session creation, participating department selection, and assigned hall configurations.
5. **Exact Seating Allocation Algorithm:** Deterministic constraint-satisfaction solver enforcing all collegiate examination rules.
6. **Pre-Allocation Audit & Validation:** Pre-flight detection of odd student parity, department 50% majority threshold violations, insufficient bench capacities, and unequal pair counts.
7. **Interactive Seating Grid Visualizer:** Two-dimensional physical bench grid displaying invigilator podium, row/column coordinates, Left Seat (Left Department student) and Right Seat (Right Department student), and explicit indicators for empty benches.
8. **Automated PDF Export:** Multi-page Master Examination Seating Plan and individual Classroom Door Notices generated via ReportLab.
9. **Rigorous Automated Test Suite:** Unit tests and web integration tests validating 100% compliance with allocation rules.

### Out-of-Scope (Future Enhancements):
- Multi-tier role-based authentication (Chief Superintendent, Invigilator, Student).
- Multi-session clash detection across consecutive examination days.
- Barcode/QR-code scanning on student hall tickets.
- Automated email/SMS notification dispatch to students.

---

## 4. Key Performance Indicators (KPIs)
- **Zero Rule Violations:** 100% guarantee that no classroom contains more than two departments and no bench seats students of the same department.
- **Sub-Second Execution:** Seating allocation calculation for multi-room cohorts in under 1 second.
- **Deterministic Reproducibility:** Repeated runs with the same input yield predictable, orderly roll-number seating sequences.
- **Zero External Proprietary Dependencies:** Entire application runs offline without paid cloud APIs, external database engines, or complex node toolchains.

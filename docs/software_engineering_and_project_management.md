# Software Engineering and Project Management

## 1. Development Methodology: Agile MVP Sprint

The ExamFlow project adopted an **Agile Iterative Sprint Methodology** tailored for accelerated delivery of high-integrity academic software. Key principles applied:
- **Test-First Correctness:** Priority placed on algorithm mathematical validity before UI decoration.
- **Incremental Layer Delivery:** Building bottom-up: SQLite persistence $\rightarrow$ core algorithm solver $\rightarrow$ PDF engine $\rightarrow$ Flask presentation $\rightarrow$ visual grid canvas.
- **Fail-Safe Contract:** The system strictly adheres to the principle that an explicit error notification is vastly superior to a flawed or fabricated result.

---

## 2. Work Breakdown Structure (WBS)

```
1.0 ExamFlow System
  ├── 1.1 Requirements & Research
  │     ├── 1.1.1 Elicit Collegiate Examination Rules
  │     └── 1.1.2 Formalize Mathematical Constraints
  ├── 1.2 Data Persistence Layer
  │     ├── 1.2.1 Design SQLite Relational Schema
  │     └── 1.2.2 Implement database.py & Connection Pools
  ├── 1.3 Seating Allocation Engine
  │     ├── 1.3.1 Formulate Pre-Validation Audit
  │     ├── 1.3.2 Implement Backtracking Search with Pruning
  │     └── 1.3.3 Implement Post-Allocation Verifier
  ├── 1.4 Document Generation Service
  │     ├── 1.4.1 Master Seating Chart ReportLab Layout
  │     └── 1.4.2 Door Notice Notice Layout
  ├── 1.5 Web Application & Presentation Layer
  │     ├── 1.5.1 Flask Endpoints & Controllers (app.py)
  │     ├── 1.5.2 CSS Design System (style.css)
  │     ├── 1.5.3 Responsive Jinja2 Templates
  │     └── 1.5.4 Interactive 2D Seating Grid (Podium, Left/Right Seats)
  ├── 1.6 Verification & Testing
  │     ├── 1.6.1 Mathematical Unit Tests (8 Cases)
  │     └── 1.6.2 Web Route Integration Tests (6 Cases)
  └── 1.7 Documentation & Project Reporting
        └── 1.7.1 IEEE SRS, System Design, and User Manual
```

---

## 3. Project Milestones & Schedule

| Milestone | Deliverable | Status | Target Date |
| :--- | :--- | :--- | :--- |
| **M1: Foundation & Schema** | Database schema created, connection factory verified. | Completed | Day 1, 09:00 |
| **M2: Algorithm Engine** | Solver and pre-validation logic passing prototype tests. | Completed | Day 1, 11:30 |
| **M3: PDF Document Generation** | Master seating plan and door notices rendering correctly. | Completed | Day 1, 13:00 |
| **M4: Web Application & UI** | Dashboard, student CSV upload, classroom forms operational. | Completed | Day 1, 15:30 |
| **M5: Seating Visualizer** | 2D bench grid with room tabs and empty bench tracking. | Completed | Day 1, 17:00 |
| **M6: Test Suite & Audit** | 14 automated tests passing with 100% success rate. | Completed | Day 1, 18:30 |
| **M7: Final Documentation** | 10 academic report chapters with UML diagrams and manual. | Completed | Day 1, 20:30 |

---

## 4. Risk Register

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **R-01** | **Incompatible Cohort Sizes:** User uploads department counts where one department exceeds 50% or total is odd. | High | Critical | Pre-allocation audit intercepts inputs before calculation, displaying an actionable mathematical explanation. |
| **R-02** | **Combinatorial Explosion:** Backtracking solver hangs on multi-classroom inputs. | Medium | High | Prune search branches immediately using 3 rules: parity check, 50% majority check on remaining counts, and cumulative remaining capacity check. |
| **R-03** | **Malformed CSV Ingestion:** User uploads missing columns, blank rows, or corrupted encodings. | High | Medium | Strict DictReader header verification, row-level error collection, and fallback to default academic year. |
| **R-04** | **Partial Allocation Crash:** Database failure during seating insertion leaves partial exam state. | Low | Critical | Wrap database inserts inside atomic SQLite transactions (`conn.commit()` / `conn.rollback()`). |
| **R-05** | **Platform Dependency Issues:** Heavy node.js or docker dependencies failing on lab Windows machines. | Medium | High | Strict stack constraint: pure Python, Flask, SQLite, Vanilla CSS/JS. Zero external binary requirements. |

---

## 5. Quality Assurance Strategy

1. **Automated Unit Testing:**
   - Isolated testing of all edge cases: odd counts, single department, unequal 2-department counts, majority threshold exceedance, capacity deficiency, and empty bench handling.
2. **Integration Route Testing:**
   - Simulated HTTP requests testing CSV ingestion, classroom CRUD, exam lifecycle transitions, and binary PDF responses.
3. **Double Verification (Post-Audit):**
   - Independent verification function (`audit`) verifies the seating assignments table for zero duplicate student IDs, zero omissions, and strict adherence to 2 departments per room.

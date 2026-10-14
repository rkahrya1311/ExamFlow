# ExamFlow: Web-Based Examination Seating Allocation System

> **A Dependable, Web-Based Examination Seating Allocation and Classroom Planning System**  
> Built strictly with **Python, Flask, SQLite, Vanilla CSS/JS, and ReportLab**.  
> Free of React, Node.js, MongoDB, Docker, paid APIs, authentication, or AI dependencies.

---

## 🚀 Quick Windows Startup Instructions

Follow these exact steps to run the application on Windows:

### Step 1: Open PowerShell
```powershell
cd d:\WAD
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Application
```powershell
python run.py
```

### Step 4: Access the System
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## ⚡ 1-Click Interactive Demo

1. Once the application opens, click the **"Seed Demo Data"** button on the top-right of the Dashboard.
2. The system instantly loads:
   - 4 Classrooms (`LH-101`, `LH-102`, `LH-201`, `LH-202`)
   - 60 Balanced students (30 CSE, 30 ECE)
   - 1 Scheduled Examination
3. Click **"View Seating Grid"** or **"Run Allocation"** to inspect the real-time mathematical audit and generated classroom seating grid!
4. Download the **Master Seating PDF** or **Classroom Door Notice PDF** with a single click.

---

## 🧪 Running Automated Tests

To run the test suite and verify 100% compliance with all real college examination rules:

```powershell
python test_suite.py
```

Expected output:
```
Ran 14 tests in 0.607s
OK
```

All 14 tests pass, validating parity checks, majority limits, capacity constraints, multi-classroom partitioning, empty benches, CSV ingestion, and PDF rendering.

---

## 🏛️ Real College Rules Enforced

ExamFlow strictly enforces collegiate anti-malpractice rules:
1. **Exactly two distinct departments per classroom:** No classroom may have only one department or a third department.
2. **Every occupied bench has exactly two students:** One student from the Left department and one from the Right department.
3. **Left/Right department orientation is strictly fixed:** Preserved throughout the entire room from front to back.
4. **Classroom capacity equals $Rows \times Columns \times 2$:** Every bench provides 2 seats.
5. **No duplicate or omitted students:** Every participating student is seated once and only once.
6. **Empty benches permitted:** If room capacity exceeds students, surplus benches remain empty while occupied benches strictly obey pairing rules.
7. **Pre-Allocation Mathematical Audit:** Instantly catches:
   - Odd student totals (cannot pair all students).
   - Single department exceeding 50% of the total student count.
   - Total classroom bench shortages.
   - Unequal cohorts in 2-department exams.
8. **Never reports success for an invalid allocation:** If mathematically impossible, displays an actionable diagnostic explanation.

---

## 📁 Repository Structure

```
d:/WAD/
├── app.py                      # Flask Application Controller & HTTP Routes
├── database.py                 # SQLite Schema, Connections & Transactions
├── allocator.py                # Mathematical Allocation Solver & Verifier
├── pdf_generator.py            # ReportLab PDF Generator (Master & Door Charts)
├── sample_data.py              # Synthetic Data Generator & Demo Seeder
├── run.py                      # Application Launcher (http://127.0.0.1:5000)
├── test_suite.py               # Complete 14-test Automated Suite
├── requirements.txt            # Python Dependencies
├── static/
│   ├── css/style.css           # Modern, Professional CSS Design System
│   └── js/main.js              # Client Interactivity, Dropzone & Tab Controls
├── templates/
│   ├── base.html               # Master Layout with Sidebar Navigation
│   ├── dashboard.html          # High-Level Metrics & Scheduled Exams
│   ├── students.html           # Student Roster, Filters & CSV Ingestion
│   ├── classrooms.html         # Room Layouts & Dynamic Capacity Calculator
│   ├── examinations.html       # Exam Event Creation & Department Selection
│   └── allocation.html         # Allocation Cockpit, Audit Card & 2D Grid
├── tests/
│   ├── test_allocator.py       # Allocation Engine Unit Tests
│   └── test_routes.py          # Integration Route Tests
└── docs/                       # Academic Project Documentation
    ├── project_overview.md
    ├── problem_statement_and_objectives.md
    ├── software_requirements_specification.md
    ├── system_design.md
    ├── database_design.md
    ├── algorithm_explanation.md
    ├── software_engineering_and_project_management.md
    ├── testing_documentation.md
    ├── user_manual.md
    └── references.md
```

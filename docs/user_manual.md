# ExamFlow User Manual & Operator Guide

Welcome to **ExamFlow**, the web-based examination seating allocation and classroom planning system. This guide provides step-by-step instructions for installation, startup, and everyday operations.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** Python 3.10 or higher
- **Web Browser:** Any modern browser (Google Chrome, Microsoft Edge, Mozilla Firefox)
- **Disk Space:** Less than 50 MB (Self-contained)

---

## 2. Installation & Quick Startup (Windows)

### Step 1: Open PowerShell or Command Prompt
Open PowerShell and navigate to the project directory:
```powershell
cd d:\WAD
```

### Step 2: Install Required Python Packages
Ensure dependencies (`Flask`, `reportlab`, `pytest`) are installed:
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Application
Launch the Flask development server:
```powershell
python run.py
```

### Step 4: Access in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 3. Operational Workflow Guide

### 3.1 Quick 1-Click Demonstration
1. On the top navigation bar of the Dashboard, click **"Seed Demo Data"**.
2. The database will automatically initialize with:
   - 4 Classrooms (`LH-101`, `LH-102`, `LH-201`, `LH-202`) with varying bench dimensions.
   - 60 Balanced Student records (30 CSE, 30 ECE).
   - 1 Pre-configured Examination (`Semester End Examinations Fall 2026`).
3. You can immediately click **"Run Allocation"** to see the system in action!

---

### 3.2 Student Directory & CSV Ingestion
1. Navigate to **"Students Directory"** from the left sidebar.
2. Filter students by department tabs (`All`, `CSE`, `ECE`, `MECH`).
3. **Download CSV Templates:**
   - Click **"Valid Sample CSV"** to get a balanced template.
   - Click **"Incompatible Sample CSV"** to test failure detection when one department exceeds 50%.
4. **Upload Custom CSV:**
   - Click **"Upload Student CSV"**.
   - Ensure your CSV has headers: `roll_number,name,department,year,email`.
   - Drag and drop or choose your file, then click **"Process & Ingest CSV"**.

---

### 3.3 Classroom Configuration
1. Click **"Classrooms"** in the sidebar.
2. View existing halls with their physical dimensions and bench capacities.
3. To add a new hall, click **"Add Classroom"**:
   - Enter **Room Number** (e.g. `Hall-301`).
   - Enter **Building** and **Floor**.
   - Enter **Rows** and **Columns** (Benches per row).
   - Observe the live **Calculated Capacity** preview:
     $$\text{Capacity} = Rows \times Columns \times 2 \text{ seats}$$
   - Click **"Save Classroom"**.

---

### 3.4 Examination Scheduling
1. Click **"Examinations"** in the sidebar.
2. Click **"Create Examination"**:
   - Provide **Title** (e.g., *Mid-Term Exams 2026*).
   - Enter **Exam Code** (e.g., *EXAM-2026-M1*).
   - Choose **Date** and **Session Timing**.
   - Check at least **two participating departments**.
   - Select the classrooms available for this examination.
   - Click **"Schedule Examination"**.

---

### 3.5 Running the Seating Allocation Engine
1. From the Examinations list or Dashboard, click **"Allocate Seating"** or **"Run Allocation"**.
2. **Review the Pre-Allocation Mathematical Audit Box:**
   - **Total Student Parity:** Must be an **Even** number.
   - **Department Diversity:** Must have at least 2 distinct departments.
   - **Majority Threshold:** No single department may exceed 50% of the students.
   - **Bench Capacity:** Total classroom benches must equal or exceed required benches ($N/2$).
3. Click **"Run Allocation Engine"**.
4. The system will:
   - Solve the room-department pairings.
   - Seat Left students and Right students deterministically by roll number.
   - Render the 2D Classroom Seating Grid!

---

### 3.6 Exploring the 2D Seating Grid
1. Use the **Classroom Tabs** (e.g. `LH-101`, `LH-102`) to view different rooms.
2. The grid displays:
   - **Front Podium / Blackboard banner** at the top.
   - Benches arranged row-by-row and column-by-column.
   - Each bench card displays:
     - Bench number (e.g. `Bench 1 [R1-C1]`).
     - **Left Seat (Blue Badge):** Roll number and student name for the Left Department.
     - **Right Seat (Green Badge):** Roll number and student name for the Right Department.
     - **Empty Benches:** Clearly designated `[ Empty Bench ]` cards if room capacity exceeds student count.

---

### 3.7 Exporting PDF Documents
1. **Master Examination Seating Plan:**
   - Click the green **"Download Master Seating PDF"** button at the top of the allocation page.
   - Produces a multi-page PDF with institutional header, summary statistics, room summaries, and complete bench-by-bench tables with invigilator signature boxes.
2. **Classroom Door Notice:**
   - In each room tab, click **"Door Notice PDF"**.
   - Produces an official Notice for display outside the hall, showing room number, left and right roll ranges, and a student seating directory.

---

## 4. Troubleshooting & FAQ

| Problem | Root Cause | Solution |
| :--- | :--- | :--- |
| **"Incompatible student count: Total student count is ODD"** | Every bench requires exactly 2 students; an odd total guarantees an unpartnered student. | Ensure an even total number of students are participating. |
| **"Department 'CSE' exceeds 50% of total students"** | A student cannot sit with someone from their own department. | Include another cohort or balance the registered numbers. |
| **"Insufficient classroom capacity"** | Available classrooms have fewer benches than required ($N/2$). | Add another classroom in the Classrooms tab and add it to the exam. |
| **"Unequal 2-department counts"** | When exactly 2 departments participate, both must have identical counts. | Equalize cohort rosters or add a 3rd department to permit flexible pairing. |

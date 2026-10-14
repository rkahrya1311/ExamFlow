"""
ExamFlow Web Application
Flask controller managing student uploads, classroom layouts, exam scheduling,
seating allocation execution, and PDF downloads.
"""

import os
import io
import csv
from typing import Dict, List, Any
from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
)
from database import get_db_connection, init_db
from allocator import generate_seating_allocation, pre_validate_exam
from pdf_generator import generate_exam_seating_pdf, generate_door_notice_pdf
from sample_data import seed_database, generate_sample_csvs

app = Flask(__name__)
app.secret_key = "examflow-super-secure-session-key-college-mvp"

# Ensure database is initialized on startup
init_db()


# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------
def fetch_departments_summary() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT department, COUNT(*) as count
        FROM students
        GROUP BY department
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_all_classrooms() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT *, (rows * columns) AS bench_capacity, (rows * columns * 2) AS seat_capacity
        FROM classrooms
        ORDER BY room_number ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# -------------------------------------------------------------------------
# Dashboard
# -------------------------------------------------------------------------
@app.route("/")
def dashboard():
    conn = get_db_connection()
    student_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    classroom_count = conn.execute("SELECT COUNT(*) FROM classrooms").fetchone()[0]
    total_capacity = conn.execute("SELECT COALESCE(SUM(rows * columns * 2), 0) FROM classrooms").fetchone()[0]
    exam_count = conn.execute("SELECT COUNT(*) FROM examinations").fetchone()[0]

    # Department breakdown
    dept_summary = fetch_departments_summary()

    # Recent examinations
    exams = conn.execute("""
        SELECT e.*,
               (SELECT COUNT(*) FROM seating_assignments WHERE exam_id = e.id) as seated_count,
               (SELECT COUNT(*) FROM room_allocations WHERE exam_id = e.id) as rooms_allocated
        FROM examinations e
        ORDER BY e.created_at DESC
        LIMIT 10
    """).fetchall()

    exam_list = []
    for ex in exams:
        ex_dict = dict(ex)
        depts = conn.execute("SELECT department FROM exam_departments WHERE exam_id = ?", (ex_dict["id"],)).fetchall()
        ex_dict["departments"] = [d["department"] for d in depts]
        exam_list.append(ex_dict)

    conn.close()

    return render_template(
        "dashboard.html",
        student_count=student_count,
        classroom_count=classroom_count,
        total_capacity=total_capacity,
        exam_count=exam_count,
        dept_summary=dept_summary,
        exams=exam_list
    )


# -------------------------------------------------------------------------
# Students Management & CSV Upload
# -------------------------------------------------------------------------
@app.route("/students")
def students_list():
    conn = get_db_connection()
    dept_filter = request.args.get("department", "")
    query = "SELECT * FROM students"
    params = []

    if dept_filter:
        query += " WHERE department = ?"
        params.append(dept_filter)

    query += " ORDER BY department, roll_number ASC"
    students = conn.execute(query, params).fetchall()

    all_depts = [r["department"] for r in conn.execute("SELECT DISTINCT department FROM students ORDER BY department").fetchall()]
    conn.close()

    return render_template("students.html", students=students, all_depts=all_depts, selected_dept=dept_filter)


@app.route("/students/upload", methods=["POST"])
def upload_students_csv():
    if "csv_file" not in request.files:
        flash("No file was uploaded.", "danger")
        return redirect(url_for("students_list"))

    file = request.files["csv_file"]
    if file.filename == "":
        flash("No file selected for upload.", "danger")
        return redirect(url_for("students_list"))

    if not file.filename.lower().endswith(".csv"):
        flash("Invalid file format. Only CSV files are accepted.", "danger")
        return redirect(url_for("students_list"))

    try:
        stream = io.StringIO(file.stream.read().decode("UTF-8", errors="replace"))
        reader = csv.DictReader(stream)

        # Normalize column header names
        if not reader.fieldnames:
            flash("Uploaded CSV file appears to be empty.", "danger")
            return redirect(url_for("students_list"))

        headers = [h.strip().lower() for h in reader.fieldnames]
        required_headers = {"roll_number", "name", "department"}

        if not required_headers.issubset(set(headers)):
            flash(f"CSV format error. Required headers missing. Expected: {', '.join(required_headers)}. Found: {', '.join(reader.fieldnames)}", "danger")
            return redirect(url_for("students_list"))

        conn = get_db_connection()
        inserted_count = 0
        skipped_count = 0
        errors = []

        for row_idx, row in enumerate(reader, start=2):
            clean_row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
            roll = clean_row.get("roll_number", "")
            name = clean_row.get("name", "")
            dept = clean_row.get("department", "").upper()
            year = clean_row.get("year", "3")
            email = clean_row.get("email", "")

            if not roll or not name or not dept:
                errors.append(f"Row {row_idx}: Missing required field (roll_number, name, or department).")
                skipped_count += 1
                continue

            try:
                year_val = int(year) if year and year.isdigit() else 3
                conn.execute("""
                    INSERT INTO students (roll_number, name, department, year, email)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(roll_number) DO UPDATE SET
                        name=excluded.name,
                        department=excluded.department,
                        year=excluded.year,
                        email=excluded.email
                """, (roll, name, dept, year_val, email))
                inserted_count += 1
            except Exception as e:
                errors.append(f"Row {row_idx} ({roll}): {str(e)}")
                skipped_count += 1

        conn.commit()
        conn.close()

        if errors:
            flash(f"Uploaded CSV with warnings: {inserted_count} student(s) imported/updated, {skipped_count} skipped. ({'; '.join(errors[:3])})", "warning")
        else:
            flash(f"Successfully imported {inserted_count} student(s) from CSV.", "success")

    except Exception as e:
        flash(f"Failed to process CSV: {str(e)}", "danger")

    return redirect(url_for("students_list"))


@app.route("/students/sample-csv/<sample_type>")
def download_sample_csv(sample_type):
    generate_sample_csvs()
    filename_map = {
        "aids_b_cse_b": "sample_aids_b_cse_b.csv",
        "valid": "sample_students_valid.csv",
        "incompatible": "sample_students_incompatible.csv",
        "odd": "sample_students_odd.csv"
    }
    filename = filename_map.get(sample_type, "sample_students_valid.csv")
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype="text/csv")
    flash("Sample file not found.", "warning")
    return redirect(url_for("students_list"))


@app.route("/students/clear", methods=["POST"])
def clear_students():
    conn = get_db_connection()
    conn.execute("DELETE FROM students")
    conn.commit()
    conn.close()
    flash("All student records have been cleared.", "info")
    return redirect(url_for("students_list"))


# -------------------------------------------------------------------------
# Classroom Management
# -------------------------------------------------------------------------
@app.route("/classrooms")
def classrooms_list():
    classrooms = fetch_all_classrooms()
    return render_template("classrooms.html", classrooms=classrooms)


@app.route("/classrooms/add", methods=["POST"])
def add_classroom():
    room_number = request.form.get("room_number", "").strip()
    building = request.form.get("building", "Academic Block").strip()
    floor = request.form.get("floor", "1").strip()
    rows = request.form.get("rows", "").strip()
    columns = request.form.get("columns", "").strip()

    if not room_number or not rows or not columns:
        flash("Room number, rows, and columns are required.", "danger")
        return redirect(url_for("classrooms_list"))

    try:
        r_val = int(rows)
        c_val = int(columns)
        f_val = int(floor) if floor.isdigit() else 1
        if r_val <= 0 or c_val <= 0:
            raise ValueError("Dimensions must be positive integers.")

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO classrooms (room_number, building, floor, rows, columns)
            VALUES (?, ?, ?, ?, ?)
        """, (room_number, building, f_val, r_val, c_val))
        conn.commit()
        conn.close()
        flash(f"Classroom '{room_number}' ({r_val}×{c_val} benches, capacity: {r_val * c_val * 2} seats) created.", "success")
    except Exception as e:
        flash(f"Error adding classroom: {str(e)}", "danger")

    return redirect(url_for("classrooms_list"))


@app.route("/classrooms/<int:classroom_id>/delete", methods=["POST"])
def delete_classroom(classroom_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM classrooms WHERE id = ?", (classroom_id,))
    conn.commit()
    conn.close()
    flash("Classroom deleted successfully.", "info")
    return redirect(url_for("classrooms_list"))


# -------------------------------------------------------------------------
# Examinations Management
# -------------------------------------------------------------------------
@app.route("/examinations")
def examinations_list():
    conn = get_db_connection()
    exams = conn.execute("""
        SELECT e.*,
               (SELECT COUNT(*) FROM seating_assignments WHERE exam_id = e.id) as seated_count,
               (SELECT COUNT(*) FROM room_allocations WHERE exam_id = e.id) as rooms_allocated
        FROM examinations e
        ORDER BY e.created_at DESC
    """).fetchall()

    all_depts = [r["department"] for r in conn.execute("SELECT DISTINCT department FROM students ORDER BY department").fetchall()]
    all_rooms = fetch_all_classrooms()

    exam_data = []
    for ex in exams:
        d_dict = dict(ex)
        depts = conn.execute("SELECT department FROM exam_departments WHERE exam_id = ?", (d_dict["id"],)).fetchall()
        d_dict["departments"] = [d["department"] for d in depts]
        exam_data.append(d_dict)

    conn.close()
    return render_template("examinations.html", exams=exam_data, all_depts=all_depts, all_rooms=all_rooms)


@app.route("/examinations/create", methods=["POST"])
def create_examination():
    title = request.form.get("title", "").strip()
    exam_code = request.form.get("exam_code", "").strip()
    date = request.form.get("date", "").strip()
    session_time = request.form.get("session_time", "").strip()
    selected_depts = request.form.getlist("departments")
    selected_rooms = request.form.getlist("classrooms")

    if not title or not exam_code or not date:
        flash("Title, Exam Code, and Date are mandatory.", "danger")
        return redirect(url_for("examinations_list"))

    if len(selected_depts) < 2:
        flash("At least 2 participating departments must be selected for an examination.", "warning")
        return redirect(url_for("examinations_list"))

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO examinations (title, exam_code, date, session_time, status)
            VALUES (?, ?, ?, ?, 'DRAFT')
        """, (title, exam_code, date, session_time or "09:30 AM - 12:30 PM"))
        exam_id = cursor.lastrowid

        for dept in selected_depts:
            cursor.execute("INSERT INTO exam_departments (exam_id, department) VALUES (?, ?)", (exam_id, dept))

        # If rooms specified, add them; else assign all available classrooms
        if not selected_rooms:
            all_rooms = conn.execute("SELECT id FROM classrooms").fetchall()
            selected_rooms = [r["id"] for r in all_rooms]

        for r_id in selected_rooms:
            cursor.execute("INSERT INTO exam_classrooms (exam_id, classroom_id) VALUES (?, ?)", (exam_id, int(r_id)))

        conn.commit()
        flash(f"Examination '{title}' ({exam_code}) scheduled with {len(selected_depts)} departments.", "success")
    except Exception as e:
        flash(f"Failed to create examination: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("examinations_list"))


@app.route("/examinations/<int:exam_id>/delete", methods=["POST"])
def delete_examination(exam_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM examinations WHERE id = ?", (exam_id,))
    conn.commit()
    conn.close()
    flash("Examination removed.", "info")
    return redirect(url_for("examinations_list"))


# -------------------------------------------------------------------------
# Allocation Engine & Visual Seating Grid
# -------------------------------------------------------------------------
@app.route("/examinations/<int:exam_id>/allocate", methods=["GET", "POST"])
def allocate_exam(exam_id):
    conn = get_db_connection()
    exam = conn.execute("SELECT * FROM examinations WHERE id = ?", (exam_id,)).fetchone()
    if not exam:
        conn.close()
        flash("Examination not found.", "danger")
        return redirect(url_for("examinations_list"))

    # Fetch participating departments
    dept_rows = conn.execute("SELECT department FROM exam_departments WHERE exam_id = ?", (exam_id,)).fetchall()
    participating_depts = [r["department"] for r in dept_rows]

    # Fetch participating classrooms
    classroom_rows = conn.execute("""
        SELECT c.*, (c.rows * c.columns) as bench_capacity, (c.rows * c.columns * 2) as seat_capacity
        FROM classrooms c
        JOIN exam_classrooms ec ON ec.classroom_id = c.id
        WHERE ec.exam_id = ?
        ORDER BY c.room_number ASC
    """, (exam_id,)).fetchall()
    classrooms_list = [dict(r) for r in classroom_rows]

    # Fetch registered students for participating departments
    students_by_dept: Dict[str, List[Dict[str, Any]]] = {}
    total_participating_students = 0
    for dept in participating_depts:
        s_rows = conn.execute("SELECT * FROM students WHERE department = ? ORDER BY roll_number ASC", (dept,)).fetchall()
        s_list = [dict(s) for s in s_rows]
        students_by_dept[dept] = s_list
        total_participating_students += len(s_list)

    dept_counts = {d: len(s) for d, s in students_by_dept.items()}

    # Run allocation on POST or display existing on GET
    allocation_result = None

    if request.method == "POST":
        # Execute the allocation algorithm
        result = generate_seating_allocation(students_by_dept, classrooms_list)
        allocation_result = result

        if result["success"]:
            # Transactionally store allocations and seating assignments in DB
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM room_allocations WHERE exam_id = ?", (exam_id,))
                cursor.execute("DELETE FROM seating_assignments WHERE exam_id = ?", (exam_id,))

                # Insert room allocations
                for ra in result["room_allocations"]:
                    cursor.execute("""
                        INSERT INTO room_allocations
                        (exam_id, classroom_id, dept_left, dept_right, benches_used, students_left_count, students_right_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        exam_id, ra["classroom_id"], ra["dept_left"], ra["dept_right"],
                        ra["benches_used"], ra["students_left_count"], ra["students_right_count"]
                    ))

                # Insert individual seating assignments
                for sa in result["seating_assignments"]:
                    cursor.execute("""
                        INSERT INTO seating_assignments
                        (exam_id, classroom_id, student_id, row_num, col_num, bench_num, seat_position, department)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        exam_id, sa["classroom_id"], sa["student_id"],
                        sa["row_num"], sa["col_num"], sa["bench_num"],
                        sa["seat_position"], sa["department"]
                    ))

                cursor.execute("""
                    UPDATE examinations
                    SET status = 'ALLOCATED', allocation_notes = ?
                    WHERE id = ?
                """, (result["message"], exam_id))

                conn.commit()
                flash("Seating allocation completed and mathematically verified against all college rules!", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Database error saving seating assignments: {str(e)}", "danger")
        else:
            # Allocation failed: Record failure note and update status
            conn.execute("""
                UPDATE examinations
                SET status = 'FAILED', allocation_notes = ?
                WHERE id = ?
            """, (result["message"], exam_id))
            conn.commit()
            flash(f"Allocation Infeasible: {result['message']}", "danger")

    # Fetch current state from DB
    current_status = conn.execute("SELECT status, allocation_notes FROM examinations WHERE id = ?", (exam_id,)).fetchone()
    exam_dict = dict(exam)
    exam_dict["status"] = current_status["status"]
    exam_dict["allocation_notes"] = current_status["allocation_notes"]

    # If allocated, retrieve structured room and seating data for display
    allocated_rooms = []
    seating_by_room = {}

    if exam_dict["status"] == "ALLOCATED":
        r_allocs = conn.execute("""
            SELECT ra.*, c.room_number, c.building, c.floor, c.rows, c.columns,
                   (c.rows * c.columns) as total_benches,
                   (c.rows * c.columns * 2) as total_capacity
            FROM room_allocations ra
            JOIN classrooms c ON c.id = ra.classroom_id
            WHERE ra.exam_id = ?
            ORDER BY c.room_number ASC
        """, (exam_id,)).fetchall()

        for ra in r_allocs:
            r_dict = dict(ra)
            c_id = r_dict["classroom_id"]

            # Fetch seating for this room
            seats = conn.execute("""
                SELECT sa.*, s.name as student_name, s.roll_number
                FROM seating_assignments sa
                JOIN students s ON s.id = sa.student_id
                WHERE sa.exam_id = ? AND sa.classroom_id = ?
                ORDER BY sa.bench_num ASC, sa.seat_position ASC
            """, (exam_id, c_id)).fetchall()

            # Group into a 2D grid: rows x columns
            rows_cnt = r_dict["rows"]
            cols_cnt = r_dict["columns"]
            grid = []
            bench_lookup = {}
            for s in seats:
                b_num = s["bench_num"]
                bench_lookup.setdefault(b_num, {})[s["seat_position"]] = dict(s)

            b_idx = 1
            for r_i in range(1, rows_cnt + 1):
                row_benches = []
                for c_i in range(1, cols_cnt + 1):
                    bench_data = {
                        "bench_num": b_idx,
                        "row": r_i,
                        "col": c_i,
                        "occupied": b_idx in bench_lookup,
                        "left": bench_lookup.get(b_idx, {}).get("LEFT"),
                        "right": bench_lookup.get(b_idx, {}).get("RIGHT")
                    }
                    row_benches.append(bench_data)
                    b_idx += 1
                grid.append(row_benches)

            r_dict["grid"] = grid
            r_dict["seat_count"] = len(seats)
            allocated_rooms.append(r_dict)

    # Perform pre-validation check to supply real-time audit cards to UI
    room_caps = [r["bench_capacity"] for r in classrooms_list]
    is_valid, check_msg, audit_data = pre_validate_exam(dept_counts, room_caps)

    conn.close()

    return render_template(
        "allocation.html",
        exam=exam_dict,
        participating_depts=participating_depts,
        classrooms=classrooms_list,
        dept_counts=dept_counts,
        total_students=total_participating_students,
        allocated_rooms=allocated_rooms,
        audit=audit_data,
        pre_valid=is_valid,
        pre_msg=check_msg
    )


# -------------------------------------------------------------------------
# PDF Export Routes
# -------------------------------------------------------------------------
@app.route("/examinations/<int:exam_id>/pdf")
def download_master_pdf(exam_id):
    conn = get_db_connection()
    exam = conn.execute("SELECT * FROM examinations WHERE id = ?", (exam_id,)).fetchone()
    if not exam:
        conn.close()
        flash("Examination not found.", "danger")
        return redirect(url_for("examinations_list"))

    if exam["status"] != "ALLOCATED":
        conn.close()
        flash("Cannot export PDF: Seating allocation has not been generated or verified.", "warning")
        return redirect(url_for("allocate_exam", exam_id=exam_id))

    room_allocs = conn.execute("""
        SELECT ra.*, c.room_number, c.rows, c.columns
        FROM room_allocations ra
        JOIN classrooms c ON c.id = ra.classroom_id
        WHERE ra.exam_id = ?
        ORDER BY c.room_number ASC
    """, (exam_id,)).fetchall()

    seating = conn.execute("""
        SELECT sa.*, s.name as student_name, s.roll_number, c.room_number
        FROM seating_assignments sa
        JOIN students s ON s.id = sa.student_id
        JOIN classrooms c ON c.id = sa.classroom_id
        WHERE sa.exam_id = ?
        ORDER BY sa.classroom_id ASC, sa.bench_num ASC, sa.seat_position ASC
    """, (exam_id,)).fetchall()

    conn.close()

    pdf_bytes = generate_exam_seating_pdf(
        dict(exam),
        [dict(r) for r in room_allocs],
        [dict(s) for s in seating]
    )

    filename = f"ExamFlow_{exam['exam_code']}_Master_Seating.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/examinations/<int:exam_id>/door-notice/<int:classroom_id>")
def download_room_door_notice(exam_id, classroom_id):
    conn = get_db_connection()
    exam = conn.execute("SELECT * FROM examinations WHERE id = ?", (exam_id,)).fetchone()
    ra = conn.execute("""
        SELECT ra.*, c.room_number, c.rows, c.columns, c.building, c.floor
        FROM room_allocations ra
        JOIN classrooms c ON c.id = ra.classroom_id
        WHERE ra.exam_id = ? AND ra.classroom_id = ?
    """, (exam_id, classroom_id)).fetchone()

    if not exam or not ra:
        conn.close()
        flash("Room allocation not found for door notice.", "danger")
        return redirect(url_for("allocate_exam", exam_id=exam_id))

    seats = conn.execute("""
        SELECT sa.*, s.name as student_name, s.roll_number
        FROM seating_assignments sa
        JOIN students s ON s.id = sa.student_id
        WHERE sa.exam_id = ? AND sa.classroom_id = ?
        ORDER BY sa.bench_num ASC, sa.seat_position ASC
    """, (exam_id, classroom_id)).fetchall()
    conn.close()

    pdf_bytes = generate_door_notice_pdf(
        dict(exam),
        dict(ra),
        [dict(s) for s in seats]
    )

    filename = f"DoorNotice_{ra['room_number']}_{exam['exam_code']}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# -------------------------------------------------------------------------
# Demonstration Quick Reset
# -------------------------------------------------------------------------
@app.route("/seed-demo", methods=["POST"])
def reset_and_seed():
    seed_database()
    flash("System successfully reset and populated with demo classrooms, balanced student lists, and draft examination.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

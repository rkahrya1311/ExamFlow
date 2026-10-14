"""
Unit Tests for ExamFlow Allocation Engine
Verifies compliance with Real College Examination Rules:
1. Exactly two distinct departments per classroom.
2. Every occupied bench has exactly two students.
3. One student belongs to each assigned department.
4. Left/right department orientation remains fixed.
5. Classroom capacity equals rows * columns * 2.
6. Students must not be duplicated or omitted.
7. No third department may appear in a classroom.
8. Detect insufficient capacity and incompatible department counts.
9. Never report success for an invalid allocation.
"""

from allocator import pre_validate_exam, generate_seating_allocation, solve_classroom_pairings


def test_pre_validation_odd_total():
    """Detect odd student count as incompatible."""
    dept_counts = {"CSE": 21, "ECE": 20}  # Total 41 (Odd)
    caps = [30]
    valid, msg, audit = pre_validate_exam(dept_counts, caps)
    assert not valid
    assert "ODD" in msg or "odd" in msg.lower()


def test_pre_validation_majority_exceeded():
    """Detect when a single department exceeds 50% across multiple departments."""
    dept_counts = {"CSE": 35, "ECE": 10, "MECH": 5}  # Total 50, CSE is 35 (70%)
    caps = [30, 30]
    valid, msg, audit = pre_validate_exam(dept_counts, caps)
    assert not valid
    assert "exceeds" in msg.lower() or "50%" in msg


def test_pre_validation_insufficient_capacity():
    """Detect when total benches required exceeds available capacity."""
    dept_counts = {"CSE": 20, "ECE": 20}  # 40 students = 20 benches needed
    caps = [15]  # Only 15 benches available
    valid, msg, audit = pre_validate_exam(dept_counts, caps)
    assert not valid
    assert "capacity" in msg.lower()


def test_pre_validation_single_department():
    """Detect failure when fewer than 2 distinct departments participate."""
    dept_counts = {"CSE": 20}
    caps = [20]
    valid, msg, audit = pre_validate_exam(dept_counts, caps)
    assert not valid
    assert "departments" in msg.lower()


def test_pre_validation_two_departments_unequal():
    """Detect failure when exactly 2 departments have unequal counts."""
    dept_counts = {"CSE": 20, "ECE": 18}
    caps = [30]
    valid, msg, audit = pre_validate_exam(dept_counts, caps)
    assert not valid
    assert "unequal" in msg.lower() or "equal" in msg.lower()


def test_valid_two_departments_allocation():
    """Tests successful allocation with 2 departments and strict bench checks."""
    students = {
        "CSE": [{"id": i, "name": f"CSE {i}", "roll_number": f"CS{i:03d}", "department": "CSE"} for i in range(1, 21)],
        "ECE": [{"id": 100 + i, "name": f"ECE {i}", "roll_number": f"EC{i:03d}", "department": "ECE"} for i in range(1, 21)]
    }
    classrooms = [
        {"id": 1, "room_number": "LH-101", "rows": 5, "columns": 4}  # 20 benches, 40 seats
    ]

    res = generate_seating_allocation(students, classrooms)
    assert res["success"] is True
    assert len(res["seating_assignments"]) == 40

    # Rule Check: Exactly 2 distinct departments
    room_alloc = res["room_allocations"][0]
    assert room_alloc["dept_left"] == "CSE"
    assert room_alloc["dept_right"] == "ECE"
    assert room_alloc["dept_left"] != room_alloc["dept_right"]

    # Rule Check: Every bench has exactly 1 left and 1 right
    benches = {}
    for s in res["seating_assignments"]:
        benches.setdefault(s["bench_num"], []).append(s)

    assert len(benches) == 20
    for b_num, seats in benches.items():
        assert len(seats) == 2
        left_seat = [s for s in seats if s["seat_position"] == "LEFT"][0]
        right_seat = [s for s in seats if s["seat_position"] == "RIGHT"][0]
        assert left_seat["department"] == "CSE"
        assert right_seat["department"] == "ECE"


def test_multi_department_multi_room_allocation():
    """
    Tests 3 departments: CSE: 30, ECE: 20, MECH: 10 (Total 60 students, 30 benches).
    Two classrooms: LH-101 (20 benches), LH-102 (15 benches). Total 35 benches > 30.
    """
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
    assert res["success"] is True
    assert len(res["seating_assignments"]) == 60

    # Verify no third department appears in any room
    for ra in res["room_allocations"]:
        c_id = ra["classroom_id"]
        room_seats = [s for s in res["seating_assignments"] if s["classroom_id"] == c_id]
        depts_in_room = set(s["department"] for s in room_seats)
        assert len(depts_in_room) == 2, f"Room {ra['room_number']} must have exactly 2 departments"
        assert ra["dept_left"] in depts_in_room
        assert ra["dept_right"] in depts_in_room

    # Verify no student omitted and no duplicates
    assigned_ids = [s["student_id"] for s in res["seating_assignments"]]
    assert len(assigned_ids) == 60
    assert len(set(assigned_ids)) == 60


def test_empty_benches_handled_validly():
    """
    Classroom has 25 benches (50 seats).
    Only 10 CSE and 10 ECE students (10 benches occupied, 15 empty).
    Empty benches are permitted and occupied benches must remain valid.
    """
    students = {
        "CSE": [{"id": i, "name": f"CSE {i}", "roll_number": f"CS{i:03d}", "department": "CSE"} for i in range(1, 11)],
        "ECE": [{"id": 50 + i, "name": f"ECE {i}", "roll_number": f"EC{i:03d}", "department": "ECE"} for i in range(1, 11)]
    }
    classrooms = [
        {"id": 1, "room_number": "LH-BIG", "rows": 5, "columns": 5}  # 25 benches
    ]

    res = generate_seating_allocation(students, classrooms)
    assert res["success"] is True
    ra = res["room_allocations"][0]
    assert ra["benches_used"] == 10
    assert ra["empty_benches"] == 15
    assert len(res["seating_assignments"]) == 20

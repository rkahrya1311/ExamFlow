"""
ExamFlow Seating Allocation Engine
Implements Real College Examination Seating Rules:
1. Exactly two distinct departments per classroom.
2. Every occupied bench has exactly two students.
3. One student belongs to each assigned department (Left Dept student, Right Dept student).
4. Left/right department orientation remains strictly fixed throughout the classroom.
5. Classroom capacity = rows * columns * 2 (rows * columns benches).
6. Students must not be duplicated or omitted.
7. No third department may appear in a classroom.
8. Empty benches are permitted if remaining rules are satisfied.
9. Pre-allocation validation detects insufficient capacity or incompatible department counts.
10. Never reports success for an invalid allocation.
"""

from typing import Dict, List, Tuple, Any, Optional
import math


class AllocationValidationError(Exception):
    """Exception raised when an examination configuration violates college rules."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


def pre_validate_exam(dept_counts: Dict[str, int], classroom_capacities: List[int]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates whether department counts and available classrooms permit a valid arrangement.
    Returns: (is_valid, reason_message, audit_data)
    """
    total_students = sum(dept_counts.values())
    total_benches_required = math.ceil(total_students / 2) if total_students > 0 else 0
    total_bench_capacity = sum(classroom_capacities)
    total_seat_capacity = total_bench_capacity * 2

    audit = {
        "total_students": total_students,
        "total_departments": len(dept_counts),
        "department_counts": dept_counts,
        "total_classrooms": len(classroom_capacities),
        "total_bench_capacity": total_bench_capacity,
        "total_seat_capacity": total_seat_capacity,
        "benches_required": total_benches_required,
        "violations": []
    }

    if total_students == 0:
        msg = "No students are registered for the selected departments."
        audit["violations"].append(msg)
        return False, msg, audit

    # Rule: Every occupied bench has exactly 2 students => total students must be even!
    if total_students % 2 != 0:
        msg = (f"Incompatible student count: Total student count is {total_students} (ODD). "
               f"Since every occupied bench must have exactly two students (one from each paired department), "
               f"an odd total guarantees at least one unpartnered student.")
        audit["violations"].append(msg)
        return False, msg, audit

    # Rule: Exactly two distinct departments per classroom => need at least 2 departments
    active_depts = {k: v for k, v in dept_counts.items() if v > 0}
    if len(active_depts) < 2:
        msg = (f"Insufficient departments: Exactly 2 distinct departments are required per classroom, "
               f"but only {len(active_depts)} department ({', '.join(active_depts.keys()) or 'None'}) has students.")
        audit["violations"].append(msg)
        return False, msg, audit

    # Specific 2-department check: if exactly 2 departments, their counts must be identical
    if len(active_depts) == 2:
        d1, d2 = list(active_depts.keys())
        c1, c2 = active_depts[d1], active_depts[d2]
        if c1 != c2:
            msg = (f"Unequal department counts: With only 2 departments participating, "
                   f"both departments must have equal numbers so every bench can be paired. Got {d1}={c1} vs {d2}={c2}.")
            audit["violations"].append(msg)
            return False, msg, audit

    # Rule: No single department can exceed 50% of the total student count
    max_dept, max_count = max(active_depts.items(), key=lambda x: x[1])
    other_sum = total_students - max_count
    if max_count > total_students // 2:
        msg = (f"Incompatible department counts: Department '{max_dept}' has {max_count} students, "
               f"which exceeds the sum of all other departments combined ({other_sum} students). "
               f"Because every bench pairs a student with a different department, at least "
               f"{max_count - other_sum} student(s) from '{max_dept}' cannot be paired.")
        audit["violations"].append(msg)
        return False, msg, audit

    # Rule: Insufficient classroom bench capacity
    if total_bench_capacity < total_students // 2:
        msg = (f"Insufficient classroom capacity: {total_students} students require {total_students // 2} benches "
               f"({total_students} seats), but the {len(classroom_capacities)} available classroom(s) provide only "
               f"{total_bench_capacity} benches ({total_seat_capacity} seats). Missing {total_students // 2 - total_bench_capacity} benches.")
        audit["violations"].append(msg)
        return False, msg, audit

    # Specific 2-department check: if exactly 2 departments, their counts must be identical
    if len(active_depts) == 2:
        d1, d2 = list(active_depts.keys())
        c1, c2 = active_depts[d1], active_depts[d2]
        if c1 != c2:
            msg = (f"Unequal 2-department counts: With only 2 departments participating, "
                   f"both departments must have equal numbers. Got {d1}={c1} vs {d2}={c2}.")
            audit["violations"].append(msg)
            return False, msg, audit

    return True, "Pre-allocation checks passed successfully.", audit


def solve_classroom_pairings(
    dept_counts: Dict[str, int],
    classroom_list: List[Dict[str, Any]]
) -> Optional[List[Dict[str, Any]]]:
    """
    Backtracking search algorithm to assign classroom to department pairs and bench counts.
    classroom_list: list of dicts with keys: {'id', 'room_number', 'rows', 'columns', 'bench_capacity'}
    Returns list of room assignments:
    [
        {
            'classroom_id': int,
            'room_number': str,
            'rows': int,
            'columns': int,
            'dept_left': str,
            'dept_right': str,
            'benches_used': int
        }, ...
    ] or None if infeasible.
    """
    # Filter active departments
    active_counts = {k: v for k, v in dept_counts.items() if v > 0}
    # Sort classrooms by capacity descending to fill large halls effectively
    sorted_rooms = sorted(classroom_list, key=lambda r: r['bench_capacity'], reverse=True)
    all_depts = sorted(active_counts.keys(), key=lambda d: active_counts[d], reverse=True)

    def search(room_idx: int, rem_counts: Dict[str, int]) -> Optional[List[Dict[str, Any]]]:
        # Check termination condition: all students assigned
        if all(cnt == 0 for cnt in rem_counts.values()):
            return []

        # Exhausted classrooms but students remain
        if room_idx >= len(sorted_rooms):
            return None

        current_room = sorted_rooms[room_idx]
        cap = current_room['bench_capacity']

        # Departments with remaining students
        current_active = [d for d in all_depts if rem_counts[d] > 0]
        if len(current_active) < 2:
            # Cannot pair if fewer than 2 departments have remaining students
            return None

        # Build department pairs, sorted by combined demand
        pairs = []
        for i in range(len(current_active)):
            for j in range(i + 1, len(current_active)):
                d1, d2 = current_active[i], current_active[j]
                # Canonical ordering: left is d1, right is d2
                pairs.append((d1, d2))
        pairs.sort(key=lambda p: rem_counts[p[0]] + rem_counts[p[1]], reverse=True)

        for d1, d2 in pairs:
            max_b = min(cap, rem_counts[d1], rem_counts[d2])
            if max_b <= 0:
                continue

            # Candidate bench allocations to explore:
            # 1. Greedy fill max_b
            # 2. Values matching exact counts of other remaining departments to avoid odd leftovers
            # 3. Decreasing steps down to 1
            candidate_benches = [max_b]
            for other_d in current_active:
                od_cnt = rem_counts[other_d]
                if 0 < od_cnt < max_b and od_cnt not in candidate_benches:
                    candidate_benches.append(od_cnt)
            # Add downstep values
            for b in range(max_b - 1, 0, -1):
                if b not in candidate_benches:
                    candidate_benches.append(b)

            for b in candidate_benches:
                new_rem = dict(rem_counts)
                new_rem[d1] -= b
                new_rem[d2] -= b

                tot_rem = sum(new_rem.values())
                # Pruning condition 1: Even total check
                if tot_rem % 2 != 0:
                    continue
                # Pruning condition 2: Max department <= 50% of remaining
                if tot_rem > 0 and any(cnt > tot_rem // 2 for cnt in new_rem.values()):
                    continue
                # Pruning condition 3: Remaining classrooms capacity >= remaining benches needed
                rem_caps = sum(r['bench_capacity'] for r in sorted_rooms[room_idx + 1:])
                if tot_rem // 2 > rem_caps:
                    continue

                sub_solution = search(room_idx + 1, new_rem)
                if sub_solution is not None:
                    assignment = {
                        'classroom_id': current_room['id'],
                        'room_number': current_room['room_number'],
                        'rows': current_room['rows'],
                        'columns': current_room['columns'],
                        'bench_capacity': current_room['bench_capacity'],
                        'dept_left': d1,
                        'dept_right': d2,
                        'benches_used': b
                    }
                    return [assignment] + sub_solution

        # Option: skip current room (leave empty) if remaining rooms have sufficient capacity
        tot_rem = sum(rem_counts.values())
        rem_caps = sum(r['bench_capacity'] for r in sorted_rooms[room_idx + 1:])
        if tot_rem // 2 <= rem_caps:
            sub_solution = search(room_idx + 1, rem_counts)
            if sub_solution is not None:
                return sub_solution

        return None

    return search(0, dict(active_counts))


def generate_seating_allocation(
    students_by_dept: Dict[str, List[Dict[str, Any]]],
    classroom_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Main allocation entrypoint.
    Executes pre-validation, pairings search, physical seating assignment, and post-allocation audit.
    Returns:
    {
        'success': bool,
        'message': str,
        'room_allocations': list,
        'seating_assignments': list,
        'audit': dict
    }
    """
    # 1. Prepare department counts
    dept_counts = {d: len(students) for d, students in students_by_dept.items()}
    room_caps = [r['rows'] * r['columns'] for r in classroom_list]

    for r in classroom_list:
        r['bench_capacity'] = r['rows'] * r['columns']

    # 2. Pre-validation
    is_valid, reason, audit = pre_validate_exam(dept_counts, room_caps)
    if not is_valid:
        return {
            'success': False,
            'message': reason,
            'room_allocations': [],
            'seating_assignments': [],
            'audit': audit
        }

    # 3. Compute Classroom Pairings
    room_assignments = solve_classroom_pairings(dept_counts, classroom_list)
    if not room_assignments:
        msg = ("Allocation infeasible: Could not find a valid arrangement of classrooms and department pairs "
               "that simultaneously satisfies room capacities and strictly two-department bench pairing rules.")
        audit["violations"].append(msg)
        return {
            'success': False,
            'message': msg,
            'room_allocations': [],
            'seating_assignments': [],
            'audit': audit
        }

    # 4. Generate Physical Seating Assignments
    # Make deep copy of student lists sorted by roll_number for deterministic, orderly seating
    student_queues = {
        d: sorted(students, key=lambda s: s['roll_number'])
        for d, students in students_by_dept.items()
    }

    final_seating = []
    final_rooms = []
    assigned_student_ids = set()

    for ra in room_assignments:
        c_id = ra['classroom_id']
        rows = ra['rows']
        cols = ra['columns']
        d_left = ra['dept_left']
        d_right = ra['dept_right']
        benches_needed = ra['benches_used']

        left_students = student_queues[d_left][:benches_needed]
        right_students = student_queues[d_right][:benches_needed]
        # Pop assigned students
        student_queues[d_left] = student_queues[d_left][benches_needed:]
        student_queues[d_right] = student_queues[d_right][benches_needed:]

        # Fill benches row-by-row
        bench_idx = 1
        for r_num in range(1, rows + 1):
            for c_num in range(1, cols + 1):
                if bench_idx <= benches_needed:
                    s_left = left_students[bench_idx - 1]
                    s_right = right_students[bench_idx - 1]

                    # Assign Left Seat
                    final_seating.append({
                        'classroom_id': c_id,
                        'room_number': ra['room_number'],
                        'student_id': s_left['id'],
                        'student_name': s_left['name'],
                        'roll_number': s_left['roll_number'],
                        'department': d_left,
                        'row_num': r_num,
                        'col_num': c_num,
                        'bench_num': bench_idx,
                        'seat_position': 'LEFT'
                    })
                    assigned_student_ids.add(s_left['id'])

                    # Assign Right Seat
                    final_seating.append({
                        'classroom_id': c_id,
                        'room_number': ra['room_number'],
                        'student_id': s_right['id'],
                        'student_name': s_right['name'],
                        'roll_number': s_right['roll_number'],
                        'department': d_right,
                        'row_num': r_num,
                        'col_num': c_num,
                        'bench_num': bench_idx,
                        'seat_position': 'RIGHT'
                    })
                    assigned_student_ids.add(s_right['id'])

                bench_idx += 1

        final_rooms.append({
            'classroom_id': c_id,
            'room_number': ra['room_number'],
            'rows': rows,
            'columns': cols,
            'dept_left': d_left,
            'dept_right': d_right,
            'benches_used': benches_needed,
            'students_left_count': benches_needed,
            'students_right_count': benches_needed,
            'total_students': benches_needed * 2,
            'capacity_benches': rows * cols,
            'empty_benches': (rows * cols) - benches_needed
        })

    # 5. POST-ALLOCATION RIGOROUS AUDIT (Guarantees zero violation before reporting success)
    audit_errors = []

    # Check 1: Exactly two distinct departments per room
    for r in final_rooms:
        if r['dept_left'] == r['dept_right']:
            audit_errors.append(f"Room {r['room_number']} has identical left and right department ({r['dept_left']}).")

    # Check 2: No third department in any room
    room_dept_map: Dict[int, set] = {}
    for s in final_seating:
        room_dept_map.setdefault(s['classroom_id'], set()).add(s['department'])
    for r_id, d_set in room_dept_map.items():
        if len(d_set) > 2:
            audit_errors.append(f"Room ID {r_id} contains {len(d_set)} departments: {d_set} (maximum 2 permitted).")

    # Check 3: Every occupied bench has exactly two students, one left, one right
    bench_map: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for s in final_seating:
        key = (s['classroom_id'], s['bench_num'])
        bench_map.setdefault(key, []).append(s)

    for (c_id, b_num), seats in bench_map.items():
        if len(seats) != 2:
            audit_errors.append(f"Classroom {c_id} Bench {b_num} has {len(seats)} student(s); must be exactly 2.")
        else:
            left_seats = [x for x in seats if x['seat_position'] == 'LEFT']
            right_seats = [x for x in seats if x['seat_position'] == 'RIGHT']
            if len(left_seats) != 1 or len(right_seats) != 1:
                audit_errors.append(f"Classroom {c_id} Bench {b_num} does not have exactly 1 LEFT and 1 RIGHT seat.")
            elif left_seats[0]['department'] == right_seats[0]['department']:
                audit_errors.append(f"Classroom {c_id} Bench {b_num} has same department on both sides: {left_seats[0]['department']}.")

    # Check 4: No student duplicated
    if len(assigned_student_ids) != len(final_seating):
        audit_errors.append(f"Duplicate student seating detected! Seats: {len(final_seating)}, Unique students: {len(assigned_student_ids)}.")

    # Check 5: No student omitted
    total_input_students = sum(dept_counts.values())
    if len(assigned_student_ids) != total_input_students:
        audit_errors.append(f"Omitted students detected! Input students: {total_input_students}, Allocated: {len(assigned_student_ids)}.")

    if audit_errors:
        audit["violations"].extend(audit_errors)
        return {
            'success': False,
            'message': f"Post-allocation verification failed: {'; '.join(audit_errors)}",
            'room_allocations': [],
            'seating_assignments': [],
            'audit': audit
        }

    audit["status"] = "VERIFIED_VALID"
    audit["allocated_students"] = len(assigned_student_ids)
    audit["allocated_benches"] = sum(r['benches_used'] for r in final_rooms)

    return {
        'success': True,
        'message': f"Allocation successfully generated and verified. Seated {len(assigned_student_ids)} students across {len(final_rooms)} classroom(s).",
        'room_allocations': final_rooms,
        'seating_assignments': final_seating,
        'audit': audit
    }

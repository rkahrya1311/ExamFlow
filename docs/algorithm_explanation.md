# Examination Seating Allocation Algorithm: Complete Technical Explanation

---

## 1. High-Level Intuitive Overview (Beginner-Friendly)

Imagine an examination hall filled with dual-seater wooden benches. Every bench has a **Left seat** and a **Right seat**.

Colleges enforce a strict anti-cheating rule:
> **"No two students sitting on the same bench may belong to the same academic department."**

Furthermore, to keep exam halls orderly and prevent invigilation confusion:
1. Each classroom can only host students from **exactly two departments** (for example, Computer Science on the left and Electronics on the right).
2. Throughout that hall, the orientation is strictly fixed: all left seats belong to Department A, and all right seats belong to Department B.
3. Every occupied bench **must have two students**—one from Department A and one from Department B. A bench cannot have only one student.
4. If a room has 20 benches, but we only have 15 pairs to seat, the first 15 benches are occupied by pairs, and the remaining 5 benches remain **empty**. Leaving benches empty is completely permitted as long as all occupied benches obey the rules.

Because every bench consumes exactly 1 student from Department A and 1 student from Department B, each classroom used always consumes an **equal number** of students from both departments!

---

## 2. Mathematical Problem Formulation

Let participating academic departments be denoted by $\mathcal{D} = \{D_1, D_2, \dots, D_m\}$ with enrolled student counts $S = (n_1, n_2, \dots, n_m)$.  
Let the total number of participating students be $N = \sum_{i=1}^m n_i$.

Let available classrooms be $\mathcal{C} = \{C_1, C_2, \dots, C_k\}$ where each classroom $C_j$ has $R_j$ rows and $W_j$ columns, yielding bench capacity $B_j = R_j \times W_j$ and seat capacity $2 B_j$.

### Formal Constraints:
1. **Total Parity Constraint:** $N \equiv 0 \pmod 2$. The total number of students must be even.
2. **Total Capacity Constraint:** $\sum_{j=1}^k B_j \ge \frac{N}{2}$. Total available bench capacity must equal or exceed required benches.
3. **Majority Threshold Constraint:** For every department $D_i \in \mathcal{D}$, $n_i \le \frac{N}{2}$.  
   *Proof:* Since every student of $D_i$ must be paired on a bench with a peer from $\mathcal{D} \setminus \{D_i\}$, the maximum number of partners available is $\sum_{p \ne i} n_p = N - n_i$. Hence $n_i \le N - n_i \iff 2n_i \le N \iff n_i \le \frac{N}{2}$.
4. **Classroom Pairing Assignment:** For each classroom $C_j$, we assign a pair $(u_j, v_j) \in \mathcal{D} \times \mathcal{D}$ ($u_j \ne v_j$) and an integer bench count $b_j \in [0, B_j]$ such that:
   $$\forall D_i \in \mathcal{D}, \quad \sum_{j: u_j = D_i \text{ or } v_j = D_i} b_j = n_i$$
   $$\sum_{j=1}^k b_j = \frac{N}{2}$$

---

## 3. Algorithm Step-by-Step Breakdown

The ExamFlow algorithm operates across four sequential phases:

```
[Phase 1: Pre-Allocation Audit]
             │
             ▼
[Phase 2: Backtracking Classroom Pairing Solver]
             │
             ▼
[Phase 3: Deterministic Physical Bench Assignment]
             │
             ▼
[Phase 4: Post-Allocation Rigorous Verification]
```

### Phase 1: Pre-Allocation Audit (`pre_validate_exam`)
Before executing any search, the system evaluates the mathematical feasibility:
- **Check 1 (Empty Cohorts):** $N > 0$.
- **Check 2 (Parity):** $N \pmod 2 == 0$. If odd, immediately raises: *"Total student count is odd. An odd total guarantees at least one unpartnered student."*
- **Check 3 (Diversity):** $|\{D_i \mid n_i > 0\}| \ge 2$. If only 1 department is present, pairing is impossible.
- **Check 4 (Equality for 2 Departments):** If $m = 2$, $n_1$ must equal $n_2$.
- **Check 5 (Majority Limit):** $\max(n_i) \le \lfloor N / 2 \rfloor$. If any department exceeds 50%, immediately details: *"Department X has $n_x$ students, exceeding sum of all other departments combined."*
- **Check 6 (Capacity):** $\sum B_j \ge N / 2$. If smaller, calculates exact shortage of benches.

### Phase 2: Backtracking Solver with Domain Pruning (`solve_classroom_pairings`)
To determine which classroom hosts which department pair and how many benches are filled:
1. Classrooms are sorted in descending order of bench capacity: $B_1 \ge B_2 \ge \dots \ge B_k$.
2. Departments are sorted by remaining student demand descending.
3. For classroom $C_j$:
   - Generate all candidate pairs of remaining departments $(d_1, d_2)$, sorted by combined demand $(rem[d_1] + rem[d_2])$.
   - Determine maximum bench filling: $M = \min(B_j, rem[d_1], rem[d_2])$.
   - Test candidate bench allocations $b \in \{M, \text{critical remainder values}, \dots, 1\}$.
4. **Domain Pruning Rules:**
   - *Prune 1:* If after subtracting $b$ from $d_1$ and $d_2$, the remaining total students is odd, prune immediately.
   - *Prune 2:* If any remaining department exceeds $50\%$ of the remaining total students, prune branch immediately.
   - *Prune 3:* If the remaining total benches required exceeds the sum of bench capacities of all remaining classrooms, prune branch immediately.
5. If assignment succeeds recursively, return the list of room allocations.

### Phase 3: Physical Bench Seating Generation
Once room pairings are determined:
1. Students within each department are sorted in ascending order of `roll_number` for predictable, fair seating.
2. For each assigned room with $b$ benches:
   - Slice the first $b$ students from Left department queue.
   - Slice the first $b$ students from Right department queue.
3. Traverse bench grid row-by-row, column-by-column ($1 \le r \le Rows$, $1 \le c \le Columns$):
   - For bench $1 \le index \le b$:
     - Assign Left Seat to student from Left Department.
     - Assign Right Seat to student from Right Department.
   - For bench $index > b$:
     - Bench marked `occupied = False` (Empty Bench).

### Phase 4: Post-Allocation Audit (Fail-Safe Verification)
Before the algorithm writes records or reports success, an independent verifier audits the generated array:
- Verifies every used room has exactly 2 unique departments.
- Verifies no 3rd department appears in any room.
- Verifies every bench has 1 Left and 1 Right student from the assigned departments.
- Verifies set of seated student IDs matches the input set with zero duplicates and zero omissions.
- If even a single discrepancy is found, rolls back and returns an error.

---

## 4. Worked Numerical Walkthroughs

### Scenario A: Three Departments Across Two Classrooms (Success)
- **Inputs:**
  - CSE: 30 students
  - ECE: 20 students
  - MECH: 10 students
  - Total students = 60 (Even $\checkmark$)
  - Majority check: CSE = 30 $\le$ 60 / 2 = 30 ($\checkmark$)
  - Classrooms:
    - Hall-101: 5 rows $\times$ 4 cols = 20 benches (40 seats)
    - Hall-102: 5 rows $\times$ 3 cols = 15 benches (30 seats)
    - Total bench capacity = 35 benches $\ge$ 30 needed ($\checkmark$)
- **Algorithm Execution:**
  - Hall-101 (cap 20): Pair (CSE, ECE). Max benches = $\min(20, 30, 20) = 20$.
    - Hall-101 takes 20 CSE and 20 ECE students (20 benches filled, 0 empty).
    - Remaining students: CSE: 10, ECE: 0, MECH: 10.
  - Hall-102 (cap 15): Pair (CSE, MECH). Max benches = $\min(15, 10, 10) = 10$.
    - Hall-102 takes 10 CSE and 10 MECH students (10 benches filled, 5 empty).
    - Remaining students: CSE: 0, ECE: 0, MECH: 0.
- **Result:** 100% allocation, zero rule violations. Hall-102 has 5 empty benches at the back.

### Scenario B: Incompatible Department Count (Detected & Prevented)
- **Inputs:**
  - CSE: 45 students
  - ECE: 15 students
  - Total students = 60 (Even)
- **Audit:**
  - Max department: CSE has 45 students.
  - Total other students = 15.
  - Pre-validation fails immediately with:
    > *"Incompatible department counts: Department 'CSE' has 45 students, which exceeds the sum of all other departments combined (15 students). At least 30 students from CSE cannot be paired."*
- **Action:** System terminates cleanly with status `FAILED` and refuses to produce an invalid allocation.

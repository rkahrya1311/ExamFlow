# Problem Statement and Objectives

## 1. Problem Statement

In higher education institutions, allocating examination seating is governed by strict anti-malpractice protocols designed to ensure academic integrity. Specifically, collegiate institutions mandate that:
1. Students from the same academic department or subject paper must not sit next to one another.
2. In typical dual-occupancy benches, each bench must be shared by exactly two students belonging to two distinct departments.
3. For operational simplicity and invigilator clarity, each classroom must host students from exactly two designated departments, maintaining a fixed left/right orientation throughout the room.

### Challenges with Current Practices:
- **High Mathematical Complexity:** Finding an assignment of classrooms to pairs of departments such that all department cohorts are completely seated while matching bench capacities is a constrained bin-packing and graph-matching problem.
- **Undetected Incompatibilities:** If one department has 55 students and the total student body is 100, manual schedulers often attempt allocation only to discover partway through that 10 students from the majority department cannot be paired.
- **High Human Error Rate:** Manual spreadsheet entries often produce unintentional seat clashes, duplicate seat assignments, or inverted left-right orientations across benches.
- **Administrative Delays:** Drafting physical notices, attendance sheets, and hall door charts by hand consumes substantial faculty time before every mid-term and semester examination.

---

## 2. Project Objectives

### Primary Objectives:
1. **Automate Seating Allocation with Exact Rule Adherence:**
   - Develop an algorithmic allocation engine that enforces all collegiate constraints without compromise.
   - Guarantee that every occupied bench has exactly one Left student and one Right student from distinct departments.
   - Enforce fixed Left/Right department orientation across each classroom.
   - Prevent any third department from entering a classroom.

2. **Provide Actionable Feasibility Auditing:**
   - Formulate pre-allocation mathematical validation checks that immediately detect odd total student parity, single-department majority threshold exceedances (> 50%), and bench capacity shortages.
   - Never report success for an invalid or incomplete allocation.

3. **Deliver an Intuitive Administrative Interface:**
   - Implement a responsive web interface allowing examination controllers to upload CSV rosters, configure physical hall layouts, and schedule examination events.
   - Provide an interactive 2D physical grid visualization displaying the front podium, bench numbers, row/column coordinates, student roll numbers, names, and department badges.

4. **Automate Document and Notice Generation:**
   - Incorporate programmatic PDF generation to produce official, print-ready Master Seating Allocation Plans and Hall Door Notices with invigilator sign-off fields.

5. **Ensure Robust Software Quality:**
   - Establish an automated test suite covering unit mathematical constraints and web integration workflows, verified with real execution results.

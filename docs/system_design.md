# System Design & Architecture

This document describes the high-level and detailed architectural design of ExamFlow, illustrating the workflow, data interactions, and components using standard UML and architectural diagrams.

---

## 1. System Architecture Diagram

```mermaid
graph TD
    Client["Web Browser (Chrome / Edge / Firefox)"]
    
    subgraph "ExamFlow Flask Application"
        Router["Flask Routing Layer (app.py)"]
        Templates["Jinja2 Presentation Engine (templates/)"]
        Static["Assets (CSS Design System, Vanilla JS)"]
        
        subgraph "Core Business Logic Services"
            Engine["Allocation Engine & Validator (allocator.py)"]
            PDFGen["PDF Document Generator (pdf_generator.py)"]
            SeedService["Demo Seeder & Utilities (sample_data.py)"]
        end
        
        DBLayer["Data Access Layer (database.py)"]
    end
    
    Database[("SQLite Database (examflow.db)")]
    
    Client -->|HTTP Requests| Router
    Router -->|Renders UI| Templates
    Templates -->|Static Assets| Static
    Router -->|Triggers Seating Solver| Engine
    Router -->|Requests Document Export| PDFGen
    Router -->|Executes DB Operations| DBLayer
    Engine -->|Reads Rosters & Rooms| DBLayer
    DBLayer -->|Reads / Writes| Database
```

---

## 2. Use Case Diagram

```mermaid
usecaseDiagram
    actor "Examination Controller" as Admin
    
    package "ExamFlow Core Operations" {
        usecase "View Analytics Dashboard" as UC1
        usecase "Upload Student CSV" as UC2
        usecase "Filter & Manage Students" as UC3
        usecase "Configure Classrooms" as UC4
        usecase "Schedule Examination" as UC5
        usecase "Review Mathematical Audit" as UC6
        usecase "Execute Seating Allocation" as UC7
        usecase "Visualize 2D Seating Grid" as UC8
        usecase "Download Master PDF" as UC9
        usecase "Download Room Door Notice PDF" as UC10
    }
    
    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
```

---

## 3. Data Flow Diagram (Level 1 DFD)

```mermaid
graph TD
    Admin["Examination Cell Officer"]
    
    CSVFile["Student CSV File"]
    P1["1.0 Parse & Validate CSV"]
    P2["2.0 Configure Halls & Grids"]
    P3["3.0 Define Examination Event"]
    P4["4.0 Audit & Allocate Seating"]
    P5["5.0 Render Seating Grid & PDF"]
    
    D1[("Students Store")]
    D2[("Classrooms Store")]
    D3[("Examinations Store")]
    D4[("Allocations Store")]
    D5[("Seating Assignments Store")]
    
    Admin -->|Uploads| CSVFile
    CSVFile --> P1
    P1 -->|Store Validated Rosters| D1
    
    Admin -->|Inputs Room Dimensions| P2
    P2 -->|Save Room Specs| D2
    
    Admin -->|Selects Cohorts & Date| P3
    P3 -->|Save Exam Schedule| D3
    
    Admin -->|Requests Allocation| P4
    D1 -->|Fetch Cohorts| P4
    D2 -->|Fetch Capacities| P4
    P4 -->|Pre-Validation & Solver| P4
    P4 -->|Save Room Pairings| D4
    P4 -->|Save Physical Seats| D5
    
    D4 --> P5
    D5 --> P5
    P5 -->|Interactive Grid UI| Admin
    P5 -->|Master PDF & Door Notices| Admin
```

---

## 4. Sequence Diagram: Allocation & Export Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Examination Officer
    participant App as Flask Router (app.py)
    participant DB as SQLite DB (database.py)
    participant Alloc as Solver (allocator.py)
    participant PDF as PDF Generator (pdf_generator.py)

    Admin->>App: POST /examinations/{id}/allocate
    App->>DB: Fetch participating student cohorts & classrooms
    DB-->>App: Return student lists & classroom capacities
    
    App->>Alloc: generate_seating_allocation(students, classrooms)
    Alloc->>Alloc: Step 1: pre_validate_exam() (Parity, 50% majority, capacities)
    
    alt Pre-Validation Failed
        Alloc-->>App: {success: False, message: "Incompatibility Explanation"}
        App->>DB: Update exam status = 'FAILED'
        App-->>Admin: Render error alert with diagnostics
    else Pre-Validation Passed
        Alloc->>Alloc: Step 2: solve_classroom_pairings() (Backtracking search)
        Alloc->>Alloc: Step 3: Populate 2D bench seats (Left & Right)
        Alloc->>Alloc: Step 4: Post-allocation rigorous verification
        Alloc-->>App: {success: True, room_allocations, seating_assignments}
        
        App->>DB: BEGIN TRANSACTION
        App->>DB: INSERT INTO room_allocations
        App->>DB: INSERT INTO seating_assignments
        App->>DB: UPDATE examinations SET status = 'ALLOCATED'
        App->>DB: COMMIT TRANSACTION
        App-->>Admin: Render 2D Seating Grid with Room Tabs
    end

    Admin->>App: GET /examinations/{id}/pdf
    App->>DB: Query verified seating assignments
    DB-->>App: Return assignment records
    App->>PDF: generate_exam_seating_pdf(exam, rooms, seats)
    PDF-->>App: Return PDF bytes
    App-->>Admin: Download ExamFlow_{code}_Master_Seating.pdf
```

---

## 5. Activity Diagram: Allocation Decision Logic

```mermaid
flowchart TD
    Start([User Initiates Allocation]) --> FetchData[Fetch Student Cohorts & Room Dimensions]
    FetchData --> CheckParity{Is Total Students Even?}
    
    CheckParity -- No --> FailParity[Fail: Odd student count guarantees unpartnered student]
    CheckParity -- Yes --> CheckDepts{Are there >= 2 Departments?}
    
    CheckDepts -- No --> FailDepts[Fail: Need at least 2 departments for bench pairing]
    CheckDepts -- Yes --> CheckMajority{Does any Dept exceed 50%?}
    
    CheckMajority -- Yes --> FailMajority[Fail: Majority department exceeds sum of all others]
    CheckMajority -- No --> CheckCap{Total Bench Cap >= Students / 2?}
    
    CheckCap -- No --> FailCap[Fail: Available classrooms lack bench capacity]
    CheckCap -- Yes --> Backtrack[Run Backtracking Classroom Solver]
    
    Backtrack --> Found{Valid Assignment Found?}
    Found -- No --> FailArrangement[Fail: Incompatible Room-Pair Packing]
    Found -- Yes --> PostAudit{Post-Allocation Audit Passes?}
    
    PostAudit -- No --> FailAudit[Fail: Internal Rule Verification Mismatch]
    PostAudit -- Yes --> CommitDB[Commit to Database & Set ALLOCATED]
    CommitDB --> RenderUI[Display 2D Grid Visualizer & Enable PDF Export]
    
    FailParity --> RecordFail[Update Exam Status = FAILED & Show Actionable Explanation]
    FailDepts --> RecordFail
    FailMajority --> RecordFail
    FailCap --> RecordFail
    FailArrangement --> RecordFail
    FailAudit --> RecordFail
    RecordFail --> Stop([End])
    RenderUI --> Stop
```

---

## 6. Class Diagram

```mermaid
classDiagram
    class Student {
        +int id
        +string roll_number
        +string name
        +string department
        +int year
        +string email
    }
    
    class Classroom {
        +int id
        +string room_number
        +string building
        +int floor
        +int rows
        +int columns
        +int bench_capacity
        +int seat_capacity
    }
    
    class Examination {
        +int id
        +string title
        +string exam_code
        +string date
        +string session_time
        +string status
        +string allocation_notes
    }
    
    class RoomAllocation {
        +int id
        +int exam_id
        +int classroom_id
        +string dept_left
        +string dept_right
        +int benches_used
        +int students_left_count
        +int students_right_count
    }
    
    class SeatingAssignment {
        +int id
        +int exam_id
        +int classroom_id
        +int student_id
        +int row_num
        +int col_num
        +int bench_num
        +string seat_position
        +string department
    }
    
    class AllocatorEngine {
        +pre_validate_exam(dept_counts, caps)
        +solve_classroom_pairings(dept_counts, rooms)
        +generate_seating_allocation(students, rooms)
    }
    
    class PDFGenerator {
        +generate_exam_seating_pdf(exam, rooms, seats)
        +generate_door_notice_pdf(exam, room, seats)
    }
    
    Examination "1" *-- "many" RoomAllocation
    Examination "1" *-- "many" SeatingAssignment
    Classroom "1" <-- "many" RoomAllocation
    Classroom "1" <-- "many" SeatingAssignment
    Student "1" <-- "many" SeatingAssignment
    AllocatorEngine ..> RoomAllocation : produces
    AllocatorEngine ..> SeatingAssignment : produces
    PDFGenerator ..> Examination : formats
```

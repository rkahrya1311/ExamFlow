"""
ExamFlow PDF Generation Module
Generates clean, professional examination seating charts and door notices using ReportLab.
"""

import io
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_exam_seating_pdf(
    exam_info: Dict[str, Any],
    room_allocations: List[Dict[str, Any]],
    seating_assignments: List[Dict[str, Any]]
) -> bytes:
    """
    Builds a multi-page comprehensive Master Seating Allocation Document.
    Returns PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569'),
        fontName='Helvetica'
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=6
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica'
    )
    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("EXAMFLOW — EXAMINATION SEATING ALLOCATION PLAN", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>{exam_info.get('title', 'Examination')}</b> | Code: <b>{exam_info.get('exam_code', 'N/A')}</b>", subtitle_style))
    story.append(Paragraph(f"Date: <b>{exam_info.get('date', 'N/A')}</b> &nbsp;|&nbsp; Session: <b>{exam_info.get('session_time', 'N/A')}</b>", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4f46e5'), spaceBefore=2, spaceAfter=12))

    # Summary Overview Card
    total_students = len(seating_assignments)
    total_rooms = len(room_allocations)
    total_benches = sum(r.get('benches_used', 0) for r in room_allocations)

    summary_data = [
        [
            Paragraph("<b>Total Students Seated</b>", cell_bold),
            Paragraph(str(total_students), cell_style),
            Paragraph("<b>Total Classrooms Used</b>", cell_bold),
            Paragraph(str(total_rooms), cell_style)
        ],
        [
            Paragraph("<b>Total Occupied Benches</b>", cell_bold),
            Paragraph(str(total_benches), cell_style),
            Paragraph("<b>Allocation Status</b>", cell_bold),
            Paragraph("<font color='#16a34a'><b>VERIFIED & COMPLIANT</b></font>", cell_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Room Allocations Summary Table
    story.append(Paragraph("Classroom Allocation Summary", section_heading))
    room_sum_rows = [[
        Paragraph("Room No.", header_style),
        Paragraph("Left Dept", header_style),
        Paragraph("Right Dept", header_style),
        Paragraph("Benches Used", header_style),
        Paragraph("Capacity", header_style),
        Paragraph("Left Students", header_style),
        Paragraph("Right Students", header_style),
        Paragraph("Total Students", header_style)
    ]]

    for r in room_allocations:
        room_sum_rows.append([
            Paragraph(f"<b>{r.get('room_number', 'N/A')}</b>", cell_style),
            Paragraph(f"<font color='#2563eb'><b>{r.get('dept_left', '')}</b></font>", cell_style),
            Paragraph(f"<font color='#059669'><b>{r.get('dept_right', '')}</b></font>", cell_style),
            Paragraph(str(r.get('benches_used', 0)), cell_style),
            Paragraph(f"{r.get('rows', 0) * r.get('columns', 0)} ({r.get('rows', 0) * r.get('columns', 0) * 2} seats)", cell_style),
            Paragraph(str(r.get('students_left_count', r.get('benches_used', 0))), cell_style),
            Paragraph(str(r.get('students_right_count', r.get('benches_used', 0))), cell_style),
            Paragraph(f"<b>{r.get('benches_used', 0) * 2}</b>", cell_bold)
        ])

    room_sum_table = Table(room_sum_rows, colWidths=[65, 65, 65, 65, 75, 60, 60, 65])
    room_sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(room_sum_table)
    story.append(Spacer(1, 16))

    # Group seating assignments by classroom
    seats_by_room: Dict[int, List[Dict[str, Any]]] = {}
    for s in seating_assignments:
        c_id = s.get('classroom_id')
        seats_by_room.setdefault(c_id, []).append(s)

    # Detailed Bench by Bench Schedule for each room
    for r in room_allocations:
        c_id = r.get('classroom_id')
        room_seats = seats_by_room.get(c_id, [])

        story.append(PageBreak())
        story.append(Paragraph(f"Classroom Seating Chart: {r.get('room_number')}", section_heading))
        story.append(Paragraph(
            f"<b>Layout:</b> {r.get('rows')} Rows × {r.get('columns')} Columns | "
            f"<b>Left Dept:</b> <font color='#2563eb'><b>{r.get('dept_left')}</b></font> | "
            f"<b>Right Dept:</b> <font color='#059669'><b>{r.get('dept_right')}</b></font> | "
            f"<b>Occupied Benches:</b> {r.get('benches_used')} / {r.get('rows', 0) * r.get('columns', 0)}",
            subtitle_style
        ))
        story.append(Spacer(1, 8))

        # Organize seats into pairs by bench_num
        bench_dict = {}
        for s in room_seats:
            b_num = s.get('bench_num')
            pos = s.get('seat_position')
            bench_dict.setdefault(b_num, {})[pos] = s

        bench_table_rows = [[
            Paragraph("Bench #", header_style),
            Paragraph("Grid (R,C)", header_style),
            Paragraph(f"LEFT SEAT ({r.get('dept_left')})<br/>Roll No. & Student Name", header_style),
            Paragraph(f"RIGHT SEAT ({r.get('dept_right')})<br/>Roll No. & Student Name", header_style),
            Paragraph("Invigilator Initials", header_style)
        ]]

        for b_num in sorted(bench_dict.keys()):
            pair = bench_dict[b_num]
            left_s = pair.get('LEFT', {})
            right_s = pair.get('RIGHT', {})

            r_num = left_s.get('row_num', right_s.get('row_num', '-'))
            c_num = left_s.get('col_num', right_s.get('col_num', '-'))

            left_desc = f"<b>{left_s.get('roll_number', '')}</b><br/>{left_s.get('student_name', '')}"
            right_desc = f"<b>{right_s.get('roll_number', '')}</b><br/>{right_s.get('student_name', '')}"

            bench_table_rows.append([
                Paragraph(f"<b>B-{b_num}</b>", cell_bold),
                Paragraph(f"R{r_num}-C{c_num}", cell_style),
                Paragraph(left_desc, cell_style),
                Paragraph(right_desc, cell_style),
                Paragraph("[ &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ]", cell_style)
            ])

        detail_table = Table(bench_table_rows, colWidths=[45, 55, 175, 175, 70])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(detail_table)
        story.append(Spacer(1, 14))

        # Invigilator Sign-off Box
        sign_data = [
            [
                Paragraph("<b>Invigilator 1 Signature:</b> ____________________", cell_style),
                Paragraph("<b>Invigilator 2 Signature:</b> ____________________", cell_style),
                Paragraph("<b>Chief Superintendent:</b> ____________________", cell_style)
            ]
        ]
        sign_table = Table(sign_data, colWidths=[170, 170, 180])
        sign_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(KeepTogether([sign_table]))

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


def generate_door_notice_pdf(
    exam_info: Dict[str, Any],
    room_allocation: Dict[str, Any],
    room_seats: List[Dict[str, Any]]
) -> bytes:
    """
    Generates a single room examination door notice to display outside the classroom.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'NoticeTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold'
    )
    room_badge_style = ParagraphStyle(
        'RoomBadge',
        parent=styles['Heading1'],
        fontSize=28,
        leading=32,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4338ca'),
        fontName='Helvetica-Bold'
    )
    meta_style = ParagraphStyle(
        'NoticeMeta',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#334155'),
        fontName='Helvetica'
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica'
    )

    story = []
    story.append(Paragraph("EXAMINATION HALL DOOR NOTICE", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>{exam_info.get('title', 'Examination')}</b> ({exam_info.get('exam_code', '')})", meta_style))
    story.append(Paragraph(f"Date: <b>{exam_info.get('date', '')}</b> &nbsp;|&nbsp; Session: <b>{exam_info.get('session_time', '')}</b>", meta_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"ROOM: {room_allocation.get('room_number', 'N/A')}", room_badge_style))
    story.append(Spacer(1, 8))

    d_left = room_allocation.get('dept_left', '')
    d_right = room_allocation.get('dept_right', '')
    left_students = [s for s in room_seats if s.get('department') == d_left]
    right_students = [s for s in room_seats if s.get('department') == d_right]

    left_rolls = sorted([s.get('roll_number', '') for s in left_students])
    right_rolls = sorted([s.get('roll_number', '') for s in right_students])

    range_left = f"{left_rolls[0]} to {left_rolls[-1]}" if left_rolls else "None"
    range_right = f"{right_rolls[0]} to {right_rolls[-1]}" if right_rolls else "None"

    overview_data = [
        [
            Paragraph(f"<b>LEFT SIDE: {d_left}</b>", ParagraphStyle('L', parent=cell_style, fontSize=11, leading=13, textColor=colors.HexColor('#1d4ed8'))),
            Paragraph(f"<b>RIGHT SIDE: {d_right}</b>", ParagraphStyle('R', parent=cell_style, fontSize=11, leading=13, textColor=colors.HexColor('#047857')))
        ],
        [
            Paragraph(f"Total Students: <b>{len(left_students)}</b><br/>Roll Range: <b>{range_left}</b>", cell_style),
            Paragraph(f"Total Students: <b>{len(right_students)}</b><br/>Roll Range: <b>{range_right}</b>", cell_style)
        ]
    ]

    overview_table = Table(overview_data, colWidths=[260, 260])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff6ff')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>STUDENT SEATING DIRECTORY</b>", styles['Heading3']))

    # Two-column directory list: Left list has Left students, Right list has Right students
    max_len = max(len(left_students), len(right_students))
    dir_rows = [[
        Paragraph(f"Bench", header_style),
        Paragraph(f"Seat", header_style),
        Paragraph(f"Roll Number", header_style),
        Paragraph(f"Student Name", header_style),
        Paragraph(f"Dept", header_style)
    ]]

    sorted_seats = sorted(room_seats, key=lambda s: (s.get('bench_num', 0), 0 if s.get('seat_position') == 'LEFT' else 1))
    for s in sorted_seats:
        dir_rows.append([
            Paragraph(f"B-{s.get('bench_num')}", cell_style),
            Paragraph(f"{s.get('seat_position')}", cell_style),
            Paragraph(f"<b>{s.get('roll_number')}</b>", cell_style),
            Paragraph(f"{s.get('student_name')}", cell_style),
            Paragraph(f"{s.get('department')}", cell_style)
        ])

    dir_table = Table(dir_rows, colWidths=[55, 55, 120, 230, 60])
    dir_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(dir_table)

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

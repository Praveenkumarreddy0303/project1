from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Student, College, Department, Semester, Subject, Marks
import random, string
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from io import BytesIO



def home(request):
    return render(request, 'app1/home.html', {
        'students': Student.objects.all(),
        'colleges': College.objects.all(),
        'departments': Department.objects.all()
    })

def generate_student_id():
    while True:
        sid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Student.objects.filter(student_id=sid).exists():
            return sid

def add_student(request):
    if request.method == "POST":
        Student.objects.create(
            student_id=generate_student_id(),
            student_name=request.POST['student_name'],
            student_age=request.POST['student_age'],
            college_id=request.POST['college'],
            dept_id=request.POST['dept'],
            joining_year=request.POST['joining_year'],
            profile_picture=request.FILES.get('profile_picture')
        )
        return redirect('home')

    return render(request, 'app1/add_student.html', {
        'colleges': College.objects.all(),
        'departments': Department.objects.all()
    })


def add_college(request):
    if request.method == "POST":
        college_name = request.POST.get('college_name')
        if college_name:
            College.objects.create(college_name=college_name)
        return redirect('home')
    return render(request, 'app1/add_college.html')

def add_department(request):
    if request.method == "POST":
        dept_name = request.POST.get('dept_name')
        if dept_name:
            Department.objects.create(dept_name=dept_name)
        return redirect('home')
    return render(request, 'app1/add_department.html')


def edit_student(request, id):
    student = get_object_or_404(Student, id=id)
    if request.method == "POST":
        student.student_name = request.POST['student_name']
        student.student_age = request.POST['student_age']
        student.college_id = request.POST['college']
        student.dept_id = request.POST['dept']
        if request.FILES.get('profile_picture'):
            student.profile_picture = request.FILES['profile_picture']
        student.save()
        return redirect('home')

    return render(request, 'app1/edit_student.html', {
        'student': student,
        'colleges': College.objects.all(),
        'departments': Department.objects.all()
    })

def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    if request.method == "POST":
        student.delete()
        return redirect('home')
    return render(request, 'app1/delete_student.html', {'student': student})

def edit_college(request, id):
    college = get_object_or_404(College, id=id)
    if request.method == "POST":
        college.college_name = request.POST['college_name']
        college.save()
        return redirect('home')
    return render(request, 'app1/edit_college.html', {'college': college})

def delete_college(request, id):
    college = get_object_or_404(College, id=id)
    if request.method == "POST":
        college.delete()
        return redirect('home')
    return render(request, 'app1/delete_college.html', {'college': college})

def edit_department(request, id):
    department = get_object_or_404(Department, id=id)
    if request.method == "POST":
        department.dept_name = request.POST['dept_name']
        department.save()
        return redirect('home')
    return render(request, 'app1/edit_department.html', {'department': department})

def delete_department(request, id):
    department = get_object_or_404(Department, id=id)
    if request.method == "POST":
        department.delete()
        return redirect('home')
    return render(request, 'app1/delete_department.html', {'department': department})

def student_profile(request, id):
    student = get_object_or_404(Student, id=id)

    current_year = datetime.now().year
    completed_semesters = max(0, (current_year - student.joining_year) * 2)

    subjects = Subject.objects.filter(
        dept=student.dept
    ).select_related("semester").order_by("semester__sem_id")

    semesters = {}
    semester_order = []

    
    for subject in subjects:
        sem = subject.semester
        if sem not in semesters:
            semesters[sem] = []
            semester_order.append(sem)

        mark, _ = Marks.objects.get_or_create(
            student=student,
            subject=subject,
            defaults={
                "marks": None,
                "remarks": "",
                "earned_credits": 0
            }
        )
        semesters[sem].append(mark)

   
    if request.method == "POST":
        semester_id = request.POST.get("semester_id")
        if semester_id:
            semester = get_object_or_404(Semester, id=semester_id)
            sem_marks = semesters.get(semester, [])

           
            for m in sem_marks:
                val = request.POST.get(f"marks_{m.id}")
                if val in ("", None):
                    return redirect("student_profile", id=id)

            for m in sem_marks:
                marks = int(request.POST.get(f"marks_{m.id}"))
                m.marks = marks
                m.remarks = "Pass" if marks >= 35 else "Fail"
                m.earned_credits = m.subject.credits if marks >= 35 else 0
                m.save()

        return redirect("student_profile", id=id)

    
    semester_data = []
    overall_subjects = 0
    overall_earned_credits = 0
    all_semesters_completed = True

    for idx, semester in enumerate(semester_order, start=1):
        sem_marks = semesters[semester]
        is_active = idx <= completed_semesters
        is_saved = all(m.marks is not None for m in sem_marks)

        if is_active and not is_saved:
            all_semesters_completed = False

        if is_active and is_saved:
            total_subjects = len(sem_marks)
            total_marks = sum(m.marks for m in sem_marks)
            total_credits = sum(m.earned_credits for m in sem_marks)
            semester_gpa = round(total_marks / total_subjects, 2)

            overall_subjects += total_subjects
            overall_earned_credits += total_credits
        else:
            total_subjects = total_marks = total_credits = semester_gpa = None

        semester_data.append({
            "semester": semester,
            "marks_list": sem_marks,
            "total_subjects": total_subjects,
            "total_marks": total_marks,
            "total_credits": total_credits,
            "semester_gpa": semester_gpa,
            "is_active": is_active,
            "is_saved": is_saved,
        })
       
        final_result = "TBA"
    
    if len(semester_order) == 8 and all_semesters_completed:
     if overall_earned_credits >= 35 :
        final_result = "Pass"
    else:
        final_result = "FAIL"

    overall_cgpa = (
        round(overall_earned_credits / overall_subjects, 2)
        if overall_subjects else None
    )

    context = {
        "student": student,
        "semester_data": semester_data,
        "overall_earned_credits": overall_earned_credits if final_result else None,
        "overall_cgpa": overall_cgpa if final_result else None,
        "final_result": final_result,
    }

    return render(request, "app1/student_profile.html", context)

def export_marks_pdf(request, id):
    student = get_object_or_404(Student, id=id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # Title
    elements.append(Paragraph(f"Student Marks Report", title_style))
    elements.append(Paragraph(f"Student Name: {student.student_name}", normal_style))
    elements.append(Paragraph(f"Student ID: {student.student_id}", normal_style))
    elements.append(Paragraph(f"Joining Year: {student.joining_year}", normal_style))
    elements.append(Paragraph(f"College: {student.college.college_name}", normal_style))
    elements.append(Paragraph(f"Department: {student.dept.dept_name}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))
    semesters = Semester.objects.all().order_by("id")

    overall_credits = 0

    for sem in semesters:
        marks_list = Marks.objects.filter(student=student, subject__semester=sem)

        if not marks_list.exists():
            continue

        elements.append(Paragraph(f"Semester {sem.sem_id}", styles["Heading3"]))
        elements.append(Spacer(1, 0.2 * inch))

        table_data = [
            ["Subject", "Marks", "Credits", "Remarks", "Earned Credits"]
        ]

        total_marks = 0
        total_credits = 0

        for m in marks_list:
            table_data.append([
                m.subject.subject_name,
                m.marks if m.marks is not None else "-",
                m.subject.credits,
                m.remarks,
                m.earned_credits
            ])

            total_marks += m.marks or 0
            total_credits += m.earned_credits or 0

        overall_credits += total_credits

       
        table = Table(table_data, colWidths=[160, 60, 60, 90, 70])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9d9d9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))

        total_subjects = marks_list.count()
        semester_gpa = round(total_marks / total_subjects, 2) if total_subjects else 0

        elements.append(Paragraph(
            f"Total Marks: {total_marks} | Total Earned Credits: {total_credits} | GPA: {semester_gpa}",
            normal_style
        ))

        elements.append(Spacer(1, 0.4 * inch))

    final_result = "Pass" if overall_credits >= 35 else "Fail"

    elements.append(Paragraph(f"Overall Earned Credits: {overall_credits}", styles["Heading3"]))
    elements.append(Paragraph(f"Final Result: {final_result}", styles["Heading2"]))

   
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.student_name}_marks.pdf"'
    response.write(pdf)

    return response

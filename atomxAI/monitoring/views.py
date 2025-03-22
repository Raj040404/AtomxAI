from django.shortcuts import render, redirect
from users.models import ExamRoom, Student
from django.utils import timezone
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json

def monitor_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        room_code = request.POST.get('room_code')

        try:
            # Fetch the exam room based on the provided room code
            exam_room = ExamRoom.objects.get(unique_code=room_code)
        except ExamRoom.DoesNotExist:
            error = "Invalid room code."
            return render(request, 'monitor.html', {'error': error})

        # Check if a student with the same roll number already exists
        existing_student = Student.objects.filter(roll_number=roll_number, exam_room=exam_room).first()
        if existing_student:
            if existing_student.name != name:
                error = "A student with this roll number already exists in this exam room. Please use the same name."
                return render(request, 'monitor.html', {'error': error})
            else:
                # Redirect to start exam if name matches
                return redirect('start_exam', room_code=room_code, roll_number=roll_number)

        try:
            # Create a new student instance
            student = Student(
                name=name,
                roll_number=roll_number,
                exam_room=exam_room,
                start_time=timezone.now()  # Store current time as datetime
            )
            student.save()
            return redirect('start_exam', room_code=room_code, roll_number=roll_number)

        except IntegrityError as e:
            error_message = str(e)
            return render(request, 'monitor.html', {'error': "Database error: " + error_message})

    return render(request, 'monitor.html')


def start_exam(request, room_code, roll_number):
    # Fetch the student and Google Form link
    try:
        student = Student.objects.get(roll_number=roll_number, exam_room__unique_code=room_code)
        exam_room = ExamRoom.objects.get(unique_code=room_code)
        google_form_link = exam_room.google_form_link
        exam_duration = exam_room.exam_duration
    except Student.DoesNotExist:
        return render(request, 'start_exam.html', {'room_code': room_code, 'error': "Student not found."})
    except ExamRoom.DoesNotExist:
        return render(request, 'start_exam.html', {'room_code': room_code, 'error': "Exam room not found."})

    if request.method == 'POST':
        # Save the end time when the student finishes the exam
        student.end_time = timezone.now()
        student.save()
        return redirect('login_signup_view')  # Redirect after ending the exam

    # If GET request, render the exam page
    return render(request, 'start_exam.html', {
        'room_code': room_code,
        'google_form_link': google_form_link,  # Pass the dynamic Google Form link
        'roll_number': roll_number,
        'exam_duration': exam_duration,
        'student': student,  # Pass the student instance to the template
    })

# views.py in monitoring app
from django.shortcuts import render, redirect
from users.models import ExamRoom, Student
from django.utils import timezone
from django.db import IntegrityError
import json

def monitor_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        room_code = request.POST.get('room_code')

        try:
            exam_room = ExamRoom.objects.get(unique_code=room_code)
        except ExamRoom.DoesNotExist:
            error = "Invalid room code."
            return render(request, 'monitor.html', {'error': error})

        existing_student = Student.objects.filter(roll_number=roll_number, exam_room=exam_room).first()
        if existing_student:
            if existing_student.name != name:
                error = "A student with this roll number already exists in this exam room. Please use the same name."
                return render(request, 'monitor.html', {'error': error})
            else:
                return redirect('start_exam', room_code=room_code, roll_number=roll_number)

        try:
            student = Student(
                name=name,
                roll_number=roll_number,
                exam_room=exam_room,
                start_time=timezone.now()
            )
            student.save()
            return redirect('start_exam', room_code=room_code, roll_number=roll_number)

        except IntegrityError as e:
            error_message = str(e)
            return render(request, 'monitor.html', {'error': "Database error: " + error_message})

    return render(request, 'monitor.html')

def start_exam(request, room_code, roll_number):
    try:
        student = Student.objects.get(roll_number=roll_number, exam_room__unique_code=room_code)
        exam_room = ExamRoom.objects.get(unique_code=room_code)
        google_form_link = exam_room.google_form_link
        exam_duration = exam_room.exam_duration
    except Student.DoesNotExist:
        return render(request, 'start_exam.html', {'room_code': room_code, 'error': "Student not found."})
    except ExamRoom.DoesNotExist:
        return render(request, 'start_exam.html', {'room_code': room_code, 'error': "Exam room not found."})

    return render(request, 'start_exam.html', {
        'room_code': room_code,
        'google_form_link': google_form_link,
        'roll_number': roll_number,
        'exam_duration': exam_duration,
        'student': student,
    })

@csrf_exempt
def end_exam(request, room_code, roll_number):
    if request.method == 'POST':
        logs = request.POST.get('log')  # Get logs from POST data

        try:
            # Parse logs from JSON
            logs = json.loads(logs)

            # Find the student based on the roll number and room code
            student = Student.objects.get(roll_number=roll_number, exam_room__unique_code=room_code)

            # Save logs and end time for the student
            student.logs = logs  # Assuming logs is a JSONField in the model
            student.end_time = timezone.now()
            student.save()

            # Redirect after ending the exam
            return redirect('login_signup_view')
        except Student.DoesNotExist:
            return render(request, 'start_exam.html', {'error': "Student not found."})
        except Exception as e:
            return render(request, 'start_exam.html', {'error': f"An error occurred: {str(e)}"})
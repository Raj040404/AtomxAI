from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from users.models import ExamRoom, Student
from django.utils import timezone
import json

def monitor_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        room_code = request.POST.get('room_code')

        try:
            exam_room = ExamRoom.objects.get(unique_code=room_code)
            student, created = Student.objects.get_or_create(
                roll_number=roll_number,
                exam_room=exam_room,
                defaults={'name': name}
            )
            if not created:
                messages.error(request, 'This roll number is already registered for this exam.')
                return render(request, 'monitor.html')
            student.start_time = timezone.now()
            student.save()
            return redirect('start_exam', room_code=room_code, roll_number=roll_number)
        except ExamRoom.DoesNotExist:
            messages.error(request, 'Invalid room code.')
            return render(request, 'monitor.html')

    return render(request, 'monitor.html')

def start_exam(request, room_code, roll_number):
    try:
        exam_room = ExamRoom.objects.get(unique_code=room_code)
        student = Student.objects.get(roll_number=roll_number, exam_room=exam_room)
        context = {
            'room_code': room_code,
            'roll_number': roll_number,
            'exam_duration': exam_room.exam_duration,
            'google_form_link': exam_room.google_form_link,
            'parsed_questions': exam_room.parsed_questions if exam_room.question_paper else None,
        }
        return render(request, 'start_exam.html', context)
    except (ExamRoom.DoesNotExist, Student.DoesNotExist):
        messages.error(request, 'Invalid exam room or student.')
        return redirect('monitor')

@csrf_exempt
def end_exam(request, room_code, roll_number):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logs = data.get('log', [])
            answers = data.get('answers', {})
            exam_room = ExamRoom.objects.get(unique_code=room_code)
            student = Student.objects.get(roll_number=roll_number, exam_room=exam_room)
            student.logs = logs
            student.end_time = timezone.now()
            student.save()

            # Save answers only if using custom form (question paper)
            if exam_room.question_paper and answers:
                from users.models import StudentQuestion
                for q_text, a_text in answers.items():
                    StudentQuestion.objects.create(
                        student=student,
                        question_text=q_text,
                        answer_text=a_text
                    )
            messages.success(request, 'Exam submitted successfully.')
            return redirect('login_signup_view')
        except (ExamRoom.DoesNotExist, Student.DoesNotExist):
            return redirect('monitor')
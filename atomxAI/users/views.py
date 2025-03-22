from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ExamRoom, Student
from .forms import ExamRoomForm
from django.http import JsonResponse

@login_required
def dashboard(request):
    user_exam_rooms = ExamRoom.objects.filter(created_by=request.user)

    total_exam_rooms = user_exam_rooms.count()
    total_students = Student.objects.filter(exam_room__created_by=request.user).count()
    recent_exams = Student.objects.filter(exam_room__created_by=request.user).order_by('-date')[:5]
    active_exam_rooms = user_exam_rooms.filter(is_active=True).count()

    if request.method == 'POST':
        form = ExamRoomForm(request.POST)
        if form.is_valid():
            exam_room = form.save(commit=False)
            exam_room.created_by = request.user
            exam_room.save()
            messages.success(request, f'Exam room created successfully! Room Code: {exam_room.unique_code}')
            return redirect('dashboard')
    else:
        form = ExamRoomForm()

    context = {
        'exam_rooms': user_exam_rooms,
        'total_exam_rooms': total_exam_rooms,
        'total_students': total_students,
        'recent_exams': recent_exams,
        'active_exam_rooms': active_exam_rooms,
        'form': form,
    }
    return render(request, 'dashboard.html', context)

@login_required
def delete_exam_room(request, exam_room_id):
    exam_room = get_object_or_404(ExamRoom, id=exam_room_id, created_by=request.user)
    exam_room.student_set.all().delete()  # Delete related students
    exam_room.delete()
    messages.success(request, 'Exam room deleted successfully.')
    return redirect('dashboard')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login_signup_view')

def get_student_logs(request):
    student_name = request.GET.get('studentName')

    if student_name:
        try:
            # Retrieve the student object
            student = Student.objects.get(name=student_name)
            logs = student.logs  # Fetch logs from the student object

            return JsonResponse({'logs': logs})  # Return logs in JSON format

        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    else:
        return JsonResponse({'error': 'No student name provided'}, status=400)

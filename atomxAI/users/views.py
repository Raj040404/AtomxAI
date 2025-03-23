from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ExamRoom, Student, StudentQuestion
from .forms import ExamRoomForm
from django.http import JsonResponse, HttpResponse
import PyPDF2
from docx import Document
from PIL import Image
import pytesseract
import os
import logging
import json

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    user_exam_rooms = ExamRoom.objects.filter(created_by=request.user)
    total_exam_rooms = user_exam_rooms.count()
    total_students = Student.objects.filter(exam_room__created_by=request.user).count()
    recent_exams = Student.objects.filter(exam_room__created_by=request.user).order_by('-date')[:5]
    active_exam_rooms = user_exam_rooms.filter(is_active=True).count()

    if request.method == 'POST':
        logger.info("Received POST request to create exam room")
        logger.info(f"POST data: {request.POST}")
        logger.info(f"FILES data: {request.FILES}")
        form = ExamRoomForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info("Form is valid")
            exam_room = form.save(commit=False)
            exam_room.created_by = request.user

            # Check if either a Google Form link or a question paper is provided
            google_form_link = form.cleaned_data['google_form_link']
            question_paper = request.FILES.get('question_paper')

            if not google_form_link and not question_paper:
                logger.warning("Neither Google Form link nor question paper provided")
                messages.error(request, 'Please provide either a Google Form link or a question paper.')
                return redirect('dashboard')

            # If a question paper is uploaded, save the object first to ensure the file is written
            if question_paper:
                logger.info(f"Processing uploaded question paper: {question_paper.name}")
                exam_room.question_paper = question_paper
                # Save the object to write the file to MEDIA_ROOT
                exam_room.save()
                try:
                    file_path = exam_room.question_paper.path
                    logger.info(f"File path: {file_path}")
                    if not os.path.exists(file_path):
                        logger.error(f"File does not exist at path: {file_path}")
                        messages.error(request, 'Uploaded file could not be found. Please try again.')
                        return redirect('dashboard')
                    if file_path.endswith('.pdf'):
                        text = extract_from_pdf(file_path)
                    elif file_path.endswith('.docx'):
                        text = extract_from_docx(file_path)
                    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
                        text = extract_from_image(file_path)
                    else:
                        logger.error("Unsupported file format")
                        messages.error(request, 'Unsupported file format. Use PDF, Word, or image.')
                        return redirect('dashboard')
                    parsed_data = parse_question_paper(text)
                    exam_room.parsed_questions = parsed_data
                    logger.info(f"Parsed questions: {parsed_data}")
                    # Save again to update parsed_questions
                    exam_room.save()
                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}")
                    messages.error(request, f'Error processing file: {str(e)}')
                    return redirect('dashboard')
            else:
                # If no question paper, ensure parsed_questions is empty
                logger.info("No question paper uploaded, setting parsed_questions to empty")
                exam_room.parsed_questions = {}
                exam_room.save()

            logger.info(f"Exam room created successfully: {exam_room.name}, Code: {exam_room.unique_code}")
            messages.success(request, f'Exam room created successfully! Room Code: {exam_room.unique_code}')
            return redirect('dashboard')
        else:
            logger.error("Form is invalid")
            logger.error(form.errors)
            messages.error(request, f'Form is invalid. Errors: {form.errors}')
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

def extract_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

def extract_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

def parse_question_paper(text):
    lines = text.split('\n')
    heading = lines[0].strip() if lines else "Unnamed Exam"
    questions = []
    for line in lines[1:]:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('Q')):
            question_text = line.split('.', 1)[1].strip() if '.' in line else line
            questions.append(question_text)
    return {"heading": heading, "questions": questions}

@login_required
def delete_exam_room(request, exam_room_id):
    exam_room = get_object_or_404(ExamRoom, id=exam_room_id, created_by=request.user)
    exam_room.student_set.all().delete()
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
            student = Student.objects.get(name=student_name)
            logs = student.logs
            return JsonResponse({'logs': logs})
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    return JsonResponse({'error': 'No student name provided'}, status=400)

def submit_answers(request, exam_room_id, student_id):
    exam_room = get_object_or_404(ExamRoom, id=exam_room_id)
    student = get_object_or_404(Student, id=student_id, exam_room=exam_room)

    questions = exam_room.parsed_questions.get('questions', [])
    if not questions:
        messages.error(request, 'No questions found for this exam room.')
        return redirect('dashboard')

    if request.method == 'POST':
        # Process the submitted answers
        for i, question in enumerate(questions, 1):
            answer = request.POST.get(f'answer_{i}', '').strip()
            if answer:  # Only save if the answer is not empty
                StudentQuestion.objects.create(
                    student=student,
                    question_text=question,
                    answer_text=answer
                )

        # Update the student's answers field for quick reference
        answers = {str(i): request.POST.get(f'answer_{i}', '') for i in range(1, len(questions) + 1)}
        student.answers = answers
        student.save()

        messages.success(request, f'Answers submitted for {student.name}.')
        return redirect('login_signup_view')  # Redirect to landing page

    context = {
        'exam_room': exam_room,
        'student': student,
        'questions': questions,
    }
    return render(request, 'test.html', context)

@login_required
def get_student_responses(request):
    student_id = request.GET.get('studentId')
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            responses = student.questions.all().values('question_text', 'answer_text')
            return JsonResponse({
                'student_name': student.name,
                'responses': list(responses)
            })
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    return JsonResponse({'error': 'No student ID provided'}, status=400)

def submit_exam_answers(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        room_code = data.get('room_code')
        roll_number = data.get('roll_number')
        answers = data.get('answers')
        question_count = data.get('question_count')

        if not room_code or not roll_number or not answers or not question_count:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        # Find the exam room and student
        exam_room = get_object_or_404(ExamRoom, unique_code=room_code)
        student = get_object_or_404(Student, roll_number=roll_number, exam_room=exam_room)

        # Get the questions from the exam room
        questions = exam_room.parsed_questions.get('questions', [])
        if not questions:
            return JsonResponse({'status': 'error', 'message': 'No questions found for this exam room'}, status=400)

        # Save the answers to StudentQuestion model
        for i in range(1, question_count + 1):
            question_index = str(i)
            if question_index in answers:
                answer = answers[question_index].strip()
                if answer:  # Only save non-empty answers
                    question_text = questions[i - 1]  # Questions are 0-indexed in the list
                    StudentQuestion.objects.create(
                        student=student,
                        question_text=question_text,
                        answer_text=answer
                    )

        # Update the student's answers field for quick reference
        student_answers = {str(i): answers.get(str(i), '') for i in range(1, question_count + 1)}
        student.answers = student_answers
        student.save()

        return JsonResponse({'status': 'success', 'message': 'Answers submitted successfully'})
    except Exception as e:
        logger.error(f"Error submitting exam answers: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def end_exam(request, room_code, roll_number):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    try:
        # Find the exam room and student
        exam_room = get_object_or_404(ExamRoom, unique_code=room_code)
        student = get_object_or_404(Student, roll_number=roll_number, exam_room=exam_room)

        # Since the answers are already submitted via /submit_exam_answers/,
        # we just need to return a success response to confirm the exam has ended
        return JsonResponse({'status': 'success', 'message': 'Exam ended successfully'})
    except Exception as e:
        logger.error(f"Error ending exam: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
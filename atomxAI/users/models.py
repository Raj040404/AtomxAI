import json
import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ExamRoom(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    google_form_link = models.URLField(default='https://www.google.com/')
    exam_duration = models.PositiveIntegerField(default=60)
    link_open_duration = models.PositiveIntegerField(default=2)
    unique_code = models.CharField(max_length=10, unique=True, blank=True)
    question_paper = models.FileField(upload_to='question_papers/', null=True, blank=True)
    parsed_questions = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        length = random.randint(5, 10)
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        while ExamRoom.objects.filter(unique_code=code).exists():
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return code

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=100)
    exam_room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True)
    warnings = models.IntegerField(default=0)
    logs = models.JSONField(default=list, blank=True)
    answers = models.JSONField(default=dict, blank=True)  # Added to store answers as a JSON object
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.logs:
            self.warnings = len(self.logs)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.exam_room.name}'

class StudentQuestion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Question for {self.student.name}: {self.question_text}'
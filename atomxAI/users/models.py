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

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        """Generate a unique code for the exam room."""
        length = random.randint(5, 10)
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        while ExamRoom.objects.filter(unique_code=code).exists():
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return code

class Student(models.Model):
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=100)
    exam_room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)  # Changed to DateTimeField
    end_time = models.DateTimeField(null=True, blank=True)    # Changed to DateTimeField
    score = models.IntegerField(null=True)
    warnings = models.IntegerField(default=0)  # Number of warnings
    logs = models.JSONField(default=list, blank=True)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Automatically set the number of logs as warnings
        if self.logs:  # Correctly check if logs is not empty
            self.warnings = len(self.logs)  # Count the number of logs
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.exam_room.name}'

from django import forms
from .models import ExamRoom

class ExamRoomForm(forms.ModelForm):
    class Meta:
        model = ExamRoom
        fields = ['name', 'google_form_link', 'exam_duration', 'link_open_duration']

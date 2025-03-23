from django import forms
from .models import ExamRoom

class ExamRoomForm(forms.ModelForm):
    question_paper = forms.FileField(
        label="Upload Question Paper (PDF, Word, or Image)",
        help_text="Optional if a Google Form link is provided.",
        required=False
    )
    google_form_link = forms.URLField(
        label="Google Form Link",
        help_text="Optional if a question paper is uploaded.",
        required=False
    )

    class Meta:
        model = ExamRoom
        fields = ['name', 'google_form_link', 'exam_duration', 'link_open_duration', 'question_paper']
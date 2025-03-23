from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('delete/<int:exam_room_id>/', views.delete_exam_room, name='delete_exam_room'),
    path('logout/', views.logout_view, name='logout'),
    path('logs/', views.get_student_logs, name='get_student_logs'),
    path('submit-answers/<int:exam_room_id>/<int:student_id>/', views.submit_answers, name='submit_answers'),
    path('get_student_responses/', views.get_student_responses, name='get_student_responses'),
    path('submit_exam_answers/', views.submit_exam_answers, name='submit_exam_answers'),
    path('exam/<str:room_code>/<str:roll_number>/end_exam/', views.end_exam, name='end_exam'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_exam_room/<int:exam_room_id>/', views.delete_exam_room, name='delete_exam_room'),
    path('logs/', views.get_student_logs, name='get_student_logs'),  # Note the trailing slash
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urls.py in 'monitoring' app
from django.urls import path
from . import views

urlpatterns = [
    path('', views.monitor_view, name='monitor'),
    path('exam/<str:room_code>/<str:roll_number>/', views.start_exam, name='start_exam'),
    path('exam/<str:room_code>/<str:roll_number>/end_exam/', views.end_exam, name='end_exam'),
]

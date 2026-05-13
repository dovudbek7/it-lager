from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home, name='home'),
    path('test/<int:test_id>/', views.student_enter, name='enter'),
    path('attempt/<int:attempt_id>/', views.take_test, name='take'),
    path('attempt/<int:attempt_id>/submit/', views.submit_test, name='submit'),
    path('result/<int:attempt_id>/', views.result_view, name='result'),

    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('teacher/logout/', views.teacher_logout, name='teacher_logout'),
    path('teacher/', views.dashboard, name='dashboard'),
    path('teacher/create/', views.create_test, name='create_test'),
    path('teacher/test/<int:test_id>/', views.edit_test, name='edit_test'),
    path('teacher/test/<int:test_id>/add-question/', views.add_question, name='add_question'),
    path('teacher/test/<int:test_id>/results/', views.test_results, name='test_results'),
    path('teacher/test/<int:test_id>/toggle/', views.toggle_test, name='toggle_test'),
    path('teacher/test/<int:test_id>/delete/', views.delete_test, name='delete_test'),
    path('teacher/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
]

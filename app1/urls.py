from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-student/', views.add_student, name='add_student'),
    path('student/<int:id>/', views.student_profile, name='student_profile'),
    path('student/edit/<int:id>/', views.edit_student, name='edit_student'),
    path('student/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('student/<int:id>/export_pdf/', views.export_marks_pdf, name='export_marks_pdf'),
    path('edit-college/<int:id>/', views.edit_college, name='edit_college'),
    path('delete-college/<int:id>/', views.delete_college, name='delete_college'),
    path('edit-department/<int:id>/', views.edit_department, name='edit_department'),
    path('delete-department/<int:id>/', views.delete_department, name='delete_department'),
]

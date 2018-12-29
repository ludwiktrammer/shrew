from django.urls import path

from .views import StudentSignupView, TeacherView, StudentPasswordResetView
app_name = 'teachers'


urlpatterns = [
    path('', TeacherView.as_view(), name='teacher'),
    path('<slug:teacher>/', StudentSignupView.as_view(), name='student-signup'),
    path('password-reset/<slug:student>/', StudentPasswordResetView.as_view(), name='password-reset'),
]

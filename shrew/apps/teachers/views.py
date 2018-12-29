from allauth.account.adapter import get_adapter
from allauth.account.utils import user_email, user_pk_to_url_str, user_username
from allauth.account.views import SignupView
from allauth.account.forms import default_token_generator
from allauth.utils import build_absolute_uri
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render, redirect
from django.test import override_settings
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from .models import Student


class StudentSignupView(SignupView):
    template_name = 'teachers/student_signup.html'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # Hide the email field
        form.fields['email'].widget = forms.HiddenInput()

        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['email_required'] = False
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = get_object_or_404(get_user_model(), username=self.kwargs['teacher'])
        return context

    def form_valid(self, *args, **kwargs):
        response = super().form_valid(*args, **kwargs)

        # Create an accompanying student object
        Student.objects.create(
            user=self.user,
            teacher=self.get_context_data()['teacher'],
        )
        return response

    # Let logged in users to see the view
    @override_settings(ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=False)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TeacherView(View):
    def get(self, request):
        if request.user.is_authenticated:
            students = Student.objects.filter(
                teacher=request.user
            ).select_related('user')
        else:
            students = Student.objects.none()

        context = {
            'students': students,
        }
        return render(request, 'teachers/teacher.html', context)


@method_decorator(login_required, name='dispatch')
class StudentPasswordResetView(View):
    def get(self, request, student):
        return redirect('teachers:teacher')

    def post(self, request, student):
        student = get_object_or_404(
            Student,
            teacher=request.user,
            user__username=student,
        )
        user = student.user

        email = user_email(request.user)

        if not email:
            messages.error(
                request,
                "Can not send a password reset link since your account ({}) doesn't have an email address associated with it.".format(request.user.username)
            )
            return redirect('teachers:teacher')

        temp_key = default_token_generator.make_token(user)
        path = reverse(
            'account_reset_password_from_key',
            kwargs={'uidb36': user_pk_to_url_str(user), 'key': temp_key},
        )
        context = {
            'current_site': get_current_site(request),
            'user': user,
            'password_reset_url': build_absolute_uri(request, path),
            'request': request,
            'username': user_username(user),
            'timeout_days': settings.PASSWORD_RESET_TIMEOUT_DAYS,
        }
        get_adapter(request).send_mail(
            'teachers/email/password_reset_key',
            email,
            context,
        )
        messages.success(
            request,
            "Password reset link for user {user} has been sent to your email address ({email})".format(
                user=user, email=email)
        )
        return redirect('teachers:teacher')

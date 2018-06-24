from django.urls import path

from .views import (
    InterpreterSandboxView,
)

app_name = 'creations'

urlpatterns = [
    path(
        '__interpreter_sandbox',
        InterpreterSandboxView.as_view(),
        name='interpreter-sandbox',
    ),
]

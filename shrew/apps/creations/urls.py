from django.urls import path

from .views import InterpreterSandboxView, EditorView, SvgPreviewView
from .api import CreationApiView

app_name = 'creations'


urlpatterns = [
    path(
        '__interpreter_sandbox',
        InterpreterSandboxView.as_view(),
        name='interpreter-sandbox',
    ),
    path(
        'api-save',
        CreationApiView.as_view(),
        name='api-save',
    ),
    path('<slug:slug>', EditorView.as_view(), name='editor-creation'),
    path('preview/<slug:slug>.svg', SvgPreviewView.as_view(), name='svg-preview'),
]

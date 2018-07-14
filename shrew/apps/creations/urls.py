from django.urls import path

from .views import (
    InterpreterSandboxView, EditorView, CreationView, SvgPreviewView, PngSocialPreviewView, ProfileView,
)
from .api import CreationApiView

app_name = 'creations'


urlpatterns = [
    path(
        '__interpreter_sandbox',
        InterpreterSandboxView.as_view(),
        name='interpreter-sandbox',
    ),
    path(
        '__api-save',
        CreationApiView.as_view(),
        name='api-save',
    ),
    path('preview/<slug:user>/<slug:slug>.svg', SvgPreviewView.as_view(), name='svg-preview'),
    path('preview/<slug:user>/<slug:slug>.png', PngSocialPreviewView.as_view(), name='png-preview'),
    path('<slug:user>/<slug:slug>/edit', EditorView.as_view(), name='editor-creation'),
    path('<slug:user>/<slug:slug>', CreationView.as_view(), name='creation-detail'),
    path('<slug:user>', ProfileView.as_view(), name='user-profile'),
]

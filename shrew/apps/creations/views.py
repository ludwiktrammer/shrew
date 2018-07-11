from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from .models import Creation


class HomePage(View):
    def get(self, request):
        drawings = Creation.objects.filter(is_animated=False, featured=True)
        animations = Creation.objects.filter(is_animated=True, featured=True)

        context = {
            'drawings': drawings,
            'animations': animations,
        }
        return render(request, 'creations/home.html', context)


class InterpreterSandboxView(View):
    def get(self, request):
        return render(request, 'creations/interpreter-sandbox.html')


class EditorView(View):
    DEFAULT_CODE = 'Circle()'

    def get(self, request, slug=None):
        if slug is not None:
            sample = get_object_or_404(Creation, slug=slug)
            code = sample.code
        else:
            code = EditorView.DEFAULT_CODE

        context = {
            'code': code,
        }
        return render(request, 'creations/editor.html', context)

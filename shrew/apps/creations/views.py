from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from .models import Sample


class HomePage(View):
    def get(self, request):
        drawings = Sample.objects.filter(kind='drawing')
        animations = Sample.objects.filter(kind='animation')

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
            sample = get_object_or_404(Sample, slug=slug)
            code = sample.code
        else:
            code = EditorView.DEFAULT_CODE

        context = {
            'code': code,
        }
        return render(request, 'creations/editor.html', context)

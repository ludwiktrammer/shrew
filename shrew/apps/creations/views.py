from django.shortcuts import render
from django.views.generic import View


class InterpreterSandboxView(View):
    def get(self, request):
        return render(request, 'creations/interpreter-sandbox.html')


class EditorView(View):
    DEFAULT_CODE = 'Circle()'

    def get(self, request):
        context = {
            'code': EditorView.DEFAULT_CODE,
        }
        return render(request, 'creations/editor.html', context)

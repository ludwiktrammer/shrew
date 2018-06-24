from django.shortcuts import render
from django.views.generic import View


class InterpreterSandboxView(View):
    def get(self, request):
        return render(request, 'creations/interpreter-sandbox.html')

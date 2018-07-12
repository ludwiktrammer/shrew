from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

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
        response = render(request, 'creations/interpreter-sandbox.html')
        response['Content-Security-Policy'] = 'sandbox allow-scripts'
        return response


@method_decorator(ensure_csrf_cookie, name='dispatch')
class EditorView(View):
    DEFAULT_CODE = 'Circle()'

    def get(self, request, slug=None):
        creation = None
        owner = False
        code = EditorView.DEFAULT_CODE

        if slug is not None:
            creation = get_object_or_404(Creation, slug=slug)
            owner = (request.user == creation.author)
            code = creation.code


        context = {
            'creation': creation,
            'code': code,
            'owner': owner,
        }
        return render(request, 'creations/editor.html', context)

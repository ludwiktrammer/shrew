from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from .models import Creation


class HomePage(View):
    def get(self, request):
        featured = Creation.objects.filter(featured=True).select_related('author')

        context = {
            'featured': featured,
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

    def get(self, request, user=None, slug=None):
        creation = None
        owner = False
        code = EditorView.DEFAULT_CODE

        if slug is not None:
            creation = get_object_or_404(Creation, author__username=user, slug=slug)
            owner = (request.user == creation.author)
            code = creation.code

        context = {
            'creation': creation,
            'code': code,
            'owner': owner,
        }
        return render(request, 'creations/editor.html', context)


class ProfileView(View):
    def get(self, request, user):
        user = get_object_or_404(get_user_model(), username=user)

        context = {
            'user': user,
        }
        return render(request, 'creations/profile.html', context)


class BackToEditorView(View):
    def get(self, request):
        return render(request, 'creations/back-to-editor.html')


class SvgPreviewView(View):
    def get(self, request, user, slug):
        creation = get_object_or_404(Creation, slug=slug, author__username=user)

        response = HttpResponse(creation.svg, content_type="image/svg+xml")
        response['Content-Security-Policy'] = 'sandbox'
        response['Content-Disposition'] = 'attachment; filename="{}.svg"'.format(slug)

        return response

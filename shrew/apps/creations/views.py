import logging

from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.cache import patch_cache_control
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Creation
from .previews import (
    PreviewRenderError, get_social_preview_url, social_preview_key, social_preview_svg,
)


logger = logging.getLogger(__name__)


class HomePage(View):
    def get(self, request):
        featured_list = Creation.objects.filter(featured=True).select_related('author')
        featured_basic = featured_list.filter(advanced=False)
        featured_advanced = featured_list.filter(advanced=True)
        paginator_basic = Paginator(featured_basic, 15)
        paginator_advanced = Paginator(featured_advanced, 15)

        context = {
            'featured_basic': paginator_basic.get_page(request.GET.get('page_basic')),
            'featured_advanced': paginator_advanced.get_page(request.GET.get('page_advanced')),
        }
        return render(request, 'creations/home.html', context)


class CreationsListView(View):
    def get(self, request):
        creations = Creation.objects.all()
        paginator_creations = Paginator(creations, 15)

        context = {
            'creations': paginator_creations.get_page(request.GET.get('page')),
        }
        return render(request, 'creations/list.html', context)


@method_decorator(xframe_options_sameorigin, name='dispatch')
class InterpreterSandboxView(View):
    def get(self, request):
        response = render(request, 'creations/interpreter-sandbox.html')
        response['Content-Security-Policy'] = 'sandbox allow-scripts'
        return response


@method_decorator(xframe_options_sameorigin, name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class EditorView(View):
    DEFAULT_CODE = 'Circle()'

    def get(self, request, user=None, slug=None):
        creation = None
        owner = False
        code = EditorView.DEFAULT_CODE
        embedded = 'embedded' in request.GET

        if slug is not None:
            creation = get_object_or_404(Creation, author__username=user, slug=slug)
            owner = (request.user == creation.author)
            code = creation.code

        context = {
            'creation': creation,
            'code': code,
            'owner': owner,
            'embedded': embedded,
        }
        template = 'creations/editor-embedded.html' if embedded else 'creations/editor.html'
        return render(request, template, context)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CreationView(View):
    def get(self, request, user, slug):
        creation = get_object_or_404(Creation, author__username=user, slug=slug)
        context = {
            'creation': creation,
            'social_preview_key': social_preview_key(creation),
            'loving_count': creation.loving.count(),
            'user_loves': creation.loving.filter(pk=request.user.pk).exists(),
        }
        return render(request, 'creations/creation.html', context)


class RemoveCreationView(View):
    def post(self, request, user, slug):
        creation = get_object_or_404(Creation, author__username=user, slug=slug)

        if creation.author != request.user:
            messages.error(request, "You don't have necessary permissions to delete '{}'".format(creation.name))
            redirect_url = creation.get_absolute_url()
        else:
            creation.delete()
            messages.success(request, "'{}' has been successfully deleted!".format(creation.name))
            redirect_url = reverse('creations:user-profile', kwargs={'user': request.user.username})

        return HttpResponseRedirect(redirect_url)


class ProfileView(View):
    def get(self, request, user):
        user = get_object_or_404(get_user_model(), username=user)

        created_paginator = Paginator(user.creations.all(), 15)
        loved_paginator = Paginator(user.loved.all(), 15)

        context = {
            'user': user,
            'created': created_paginator.get_page(request.GET.get('page_created')),
            'loved': loved_paginator.get_page(request.GET.get('page_loved')),
        }
        return render(request, 'creations/profile.html', context)


class BackToEditorView(View):
    def get(self, request):
        return render(request, 'creations/back-to-editor.html')


class SvgPreviewView(View):
    def get(self, request, user, slug):
        creation = get_object_or_404(Creation, slug=slug, author__username=user)
        svg = creation.svg

        if 'facebook' in request.GET:
            svg = social_preview_svg(creation)

        response = HttpResponse(svg, content_type="image/svg+xml")
        response['Content-Security-Policy'] = 'sandbox'
        response['Content-Disposition'] = 'attachment; filename="{}.svg"'.format(slug)

        return response


class PngSocialPreviewView(View):
    def get(self, request, user, slug):
        creation = get_object_or_404(Creation, slug=slug, author__username=user)

        try:
            output_url = get_social_preview_url(creation)
        except (PreviewRenderError, OSError):
            logger.exception('Could not render social preview for creation %s', creation.pk)
            response = HttpResponse('Preview temporarily unavailable.', status=503)
            response['Retry-After'] = '60'
            response['Cache-Control'] = 'no-store'
            return response

        response = HttpResponseRedirect(output_url)
        patch_cache_control(response, public=True, max_age=300)
        return response

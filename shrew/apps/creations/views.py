import cloudconvert
from contact_form.forms import ReCaptchaContactForm

from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.utils.dateformat import format
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Creation


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
            svg = svg.replace('viewBox="0 0 100 100"', 'viewBox="-45.25 0 190.5 100"', 1)  # make it wider
            if creation.is_animated:
                play_svg = render_to_string('creations/_play.svg')
                svg = svg.replace('</svg>', play_svg + '\n</svg>')

        response = HttpResponse(svg, content_type="image/svg+xml")
        response['Content-Security-Policy'] = 'sandbox'
        response['Content-Disposition'] = 'attachment; filename="{}.svg"'.format(slug)

        return response


class PngSocialPreviewView(View):
    def get(self, request, user, slug):
        creation = get_object_or_404(Creation, slug=slug, author__username=user)

        cache_key = 'png_url;{};{};{}'.format(
            creation.author,
            creation.slug,
            format(creation.last_modified, 'U'),
        )

        output_url = cache.get(cache_key)
        if output_url is None:
            svg_path = reverse(
                'creations:svg-preview',
                kwargs={'user': creation.author, 'slug': creation.slug},
            )
            api = cloudconvert.Api(settings.CLOUDCONVERT_KEY)

            input_url = '{}?facebook'.format(request.build_absolute_uri(svg_path))
            process = api.convert({
                "inputformat": "svg",
                "outputformat": "png",
                "input": "download",
                "file": input_url,
                "converteroptions": {
                    "resize": "1200x630"
                },
                "save": True,
            })
            output_url = process['output']['url']
            cache.set(cache_key, output_url, 60 * 60 * 23.5)  # keep for 23.5 hours

        return HttpResponseRedirect(output_url)


class AboutView(View):
    def get(self, request):
        context = {
            'contact_form': ReCaptchaContactForm(request=request),
        }

        return render(request, 'about.html', context)

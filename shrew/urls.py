"""shrew URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.static import static

from contact_form.views import ContactFormView

from shrew.apps.creations.views import EditorView, HomePage, BackToEditorView
from shrew.apps.about.forms import ShrewContactForm
from shrew.apps.about.views import AboutView

admin.site.site_header = 'Code Shrew Admin'

urlpatterns = [
    path('', HomePage.as_view()),
    path('contact/', ContactFormView.as_view(form_class=ShrewContactForm), name='contact_form'),
    path('contact/sent/', TemplateView.as_view(template_name='contact_form/contact_form_sent.html'), name='contact_form_sent'),
    path('about/', AboutView.as_view(), name='about'),
    path('accounts/', include('allauth.urls')),
    path('todo/', TemplateView.as_view(template_name='todo.html'), name='todo'),
    path('show/', include('shrew.apps.creations.urls')),
    path('edu/', include('shrew.apps.teachers.urls')),
    path('admin/', admin.site.urls),
    path('editor/', EditorView.as_view(), name='editor'),
    path('back-to-editor/', BackToEditorView.as_view(), name='back-to-editor'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
    path('', include('shrew.apps.pages.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

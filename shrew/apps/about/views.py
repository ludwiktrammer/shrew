from django.shortcuts import render
from django.views.generic import View

from .forms import ShrewContactForm

class AboutView(View):
    def get(self, request):
        context = {
            'contact_form': ShrewContactForm(request=request),
        }

        return render(request, 'about.html', context)

from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from .models import Page, PageCategory


class PageDetailView(View):
    def get(self, request, slug, category_slug=None):

        page = get_object_or_404(
            Page,
            slug=slug,
            category__slug=category_slug,
        )

        context = {
            'page': page,
        }

        return render(request, 'pages/page-detail.html', context)



class PageCategoryDetailView(View):
    def get(self, request, slug):
        category = get_object_or_404(
            PageCategory,
            slug=slug,
        )
        pages = Page.objects.filter(
            visible=True,
            category=category,
        )

        context = {
            'category': category,
            'pages': pages,
        }

        return render(request, 'pages/category-detail.html', context)

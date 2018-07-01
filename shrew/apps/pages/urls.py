from django.urls import path

from .views import PageDetailView, PageCategoryDetailView

app_name = 'pages'

urlpatterns = [
    path(
        '<slug:slug>/',
        PageCategoryDetailView.as_view(),
        name='category-detail',
    ),
    path(
        '<slug:category_slug>/<slug:slug>/',
        PageDetailView.as_view(),
        name='page-detail',
    ),
    path(
        'page/<slug:slug>/',
        PageDetailView.as_view(),
        name='page-detail',
    ),
]

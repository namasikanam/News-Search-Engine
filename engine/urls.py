from django.urls import path
from . import views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('', views.index, name='main-page'),
    path('search', views.search, name="search"),
    path('detail/<str:id>', views.detail, name='detail'),
]

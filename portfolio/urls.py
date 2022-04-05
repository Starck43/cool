from django.urls import path, re_path
from . import views

app_name = 'portfolio'

urlpatterns = [
	path('', views.index, name='index'),
	path('reset_cache', views.reset_cache, name='reset-cache'),
]

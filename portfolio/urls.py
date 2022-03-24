from django.urls import path, re_path
from . import views

app_name = 'portfolio'

urlpatterns = [
	path('', views.index, name='index'),
	#path('portfolio/',views.portfolio_list.as_view(), kwargs={'slug': None}, name='portfolio-list-url'),
	#path('portfolio/<slug>/',views.portfolio_list.as_view(), name='portfolio-list-url'),
	#path('portfolio/<slug>/',views.portfolio_detail.as_view(), name='portfolio-detail-url'),
]

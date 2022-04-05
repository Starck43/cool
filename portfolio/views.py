from os import path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

#from django import forms
from .models import Contact, Service, Portfolio, Image
from .logic import clear_cache



""" Drop off site cache """
@login_required
def reset_cache(request):
	clear_cache()
	return HttpResponse(f'<h1>Кэш страницы сброшен!</h1><br/><a href="/"><< Назад</a>')




""" Main page """
@cache_page(6*30*24*60*60)
def index(request):
	contact = Contact.objects.all()[0]
	service = Service.objects.all()
	scheme = request.is_secure() and "https" or "http"
	site_url = '%s://%s' % (scheme, request.META['HTTP_HOST'])

	context = {
		'html_classes': ['home'],
		'contact': contact,
		'service_list' : service,
		'site_url': site_url,
	}

	return render(request, 'index.html', context)


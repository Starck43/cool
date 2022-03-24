from os import path

from django.conf import settings
from django.shortcuts import render #, redirect, HttpResponseRedirect

#from django.urls import reverse_lazy
#from django.dispatch import receiver

#from django.db.models import Q, OuterRef, Subquery, Prefetch, Max, Count, Avg
#from django.db.models.expressions import F, Value
#from django.db.models.functions import Coalesce

#from django.utils.timezone import now
#from django.utils.decorators import method_decorator

from django.views.generic.list import ListView
#from django.views.generic.detail import DetailView

#from django import forms
from .models import Contact, Service, Portfolio, Image


""" Main page """
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


""" Portfolio ListView """
class portfolio_list(ListView):
	model = Portfolio
	template_name = 'portfolio/portfolio_list.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['html_classes'] = ['portfolio-list',]
		return context

from django.contrib import admin
from django.urls import path, re_path, include

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

#from django.contrib.sitemaps.views import sitemap
#from .sitemap import sitemaps

urlpatterns = [
	re_path(r'^admin/', admin.site.urls),
	path('', include('portfolio.urls')),
	#path('accounts/', include('allauth.urls')),
	#re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
	#re_path(r'^chaining/', include('smart_selects.urls')),
	#re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
	path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	import debug_toolbar
	urlpatterns = [
		path('__debug__/', include(debug_toolbar.urls)),
	] + urlpatterns

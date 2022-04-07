from django.contrib import admin
from django.core.cache import caches

# Register your models here.
from .models import *
from .logic import get_image_html, clear_cache

from sorl.thumbnail.admin import AdminImageMixin



class ImagesInline(admin.TabularInline):
	#form = ImageForm
	model = Image
	extra = 1 #new blank record count
	show_change_link = True
	readonly_fields = ('file_thumb',)
	fields = ('file_thumb', 'file', 'title', 'general',)
	list_display = ('file_thumb', 'title', 'general')
	list_editable = ['title','general']



@admin.register(Image)
class ImageAdmin(AdminImageMixin, admin.ModelAdmin):
	#fields = ('portfolio', 'title', 'excerpt', 'file', 'general')
	list_display = ('file_thumb', 'portfolio', 'title', 'general')
	list_display_links = ('file_thumb', 'portfolio', 'title',)
	list_per_page = 30

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		clear_cache()



@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
	list_display = ('thumb', '__str__', 'service', 'created',)
	list_display_links = ('thumb', '__str__',)
	search_fields = ('title',)
	list_filter = ('service',)
	inlines = [ImagesInline]

	list_per_page = 30
	save_as = True

	def thumb(self, obj):
		image = obj.images.filter(general=True)
		thumb_file = image[0].file if image else None
		return get_image_html(thumb_file)
	thumb.short_description = 'Обложка'

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		clear_cache()



@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
	prepopulated_fields = {"map_url": ('address',)}

	list_display = ('file_thumb', 'name',)
	list_display_links = ('file_thumb', 'name',)

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		clear_cache()



@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
	exclude = ('seo_title','seo_description', 'seo_keywords')


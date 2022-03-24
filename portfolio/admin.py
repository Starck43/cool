from django.contrib import admin

# Register your models here.
from .models import *

from sorl.thumbnail.admin import AdminImageMixin


class ImagesInline(admin.TabularInline):
	#form = ImageForm
	model = Image
	extra = 1 #new blank record count
	show_change_link = True
	readonly_fields = ('file_thumb',)
	fields = ('file_thumb', 'title', 'general',)
	list_display = ('file_thumb', 'title', 'general')
	list_editable = ['title','general']


@admin.register(Image)
class ImageAdmin(AdminImageMixin, admin.ModelAdmin):
	#fields = ('portfolio', 'title', 'excerpt', 'file', 'general')
	list_display = ('file_thumb', 'portfolio', 'title', 'general')
	list_display_links = ('file_thumb', 'portfolio', 'title',)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'service', 'created',)
	inlines = [ImagesInline]

	list_per_page = 30
	save_on_top = True # adding save button on top bar
	save_as = True
	view_on_site = True


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
	prepopulated_fields = {"map_url": ('address',)}

	list_display = ('file_thumb', 'name',)
	list_display_links = ('file_thumb', 'name',)



admin.site.register(Service)

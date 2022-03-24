import re
from os import path, remove
from sys import getsizeof
from PIL import ImageFile, Image as Im
from io import BytesIO

from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.utils.html import format_html
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadhandler import MemoryFileUploadHandler

from sorl.thumbnail import get_thumbnail
from uuslug import slugify


ImageFile.LOAD_TRUNCATED_IMAGES = True

DEFAULT_SIZE = getattr(settings, 'DJANGORESIZED_DEFAULT_SIZE', [1500, 1024])
DEFAULT_QUALITY = getattr(settings, 'DJANGORESIZED_DEFAULT_QUALITY', 85)
DEFAULT_KEEP_META = getattr(settings, 'DJANGORESIZED_DEFAULT_KEEP_META', False)


class ImageUploadHandler(MemoryFileUploadHandler):
	def file_complete(self, file_size):
		if self.content_type and 'image' in self.content_type:
			self.file.seek(0)
			image = Im.open(self.file)
			width, height = image.size

			if width > DEFAULT_SIZE[0] or height > DEFAULT_SIZE[1] or 'png' in self.content_type:
				output = BytesIO()

				if image.mode != 'RGB':
					image = image.convert('RGB')

				if self.field_name in ['logo','map_thumb']:
					image.thumbnail([300,300], Im.ANTIALIAS)
				else:
					image.thumbnail(DEFAULT_SIZE, Im.ANTIALIAS)

				meta = image.info
				if not DEFAULT_KEEP_META:
					meta.pop('exif', None)

				image.save(output, format='JPEG', quality=DEFAULT_QUALITY, optimize=True, **meta)

				self.file = output
				self.content_type = 'image/jpeg'
				filename, ext = path.splitext(self.file_name)
				self.file_name = '{0}.{1}'.format(filename, 'jpg')

		return super().file_complete(file_size)



class MediaFileStorage(FileSystemStorage):
	def __init__(self, **kwargs):
		self.output_name = kwargs.get('output', None)
		super().__init__()


	def get_available_name(self, name, max_length=None):
		if self.output_name:
			name = self.output_name
		else:
			filename, ext = path.splitext(name)
			name = slugify(filename)+ext

		if path.exists(self.path(name)):
			remove(self.path(name))

		return name




""" portfolio files will be uploaded to MEDIA_ROOT/uploads/<porfolio>/<filename> """
def PortfolioUploadTo(instance, filename):
	return '{0}{1}/{2}'.format(settings.FILES_UPLOAD_FOLDER, instance.portfolio.slug, filename)



def get_image_html(obj):
	if obj and path.isfile(path.join(settings.MEDIA_ROOT,obj.name)):
		size = '%sx%s' % (settings.ADMIN_THUMBNAIL_SIZE[0], settings.ADMIN_THUMBNAIL_SIZE[1])
		thumb = get_thumbnail(obj.name, size, crop='center', quality=settings.ADMIN_THUMBNAIL_QUALITY)
		return format_html('<img src="{0}" width="50"/>', thumb.url)
	else:
		return format_html('<img src="/media/no-image.png" width="50"/>')



""" Image file size validator """
def limit_file_size(file):
	limit = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
	if path.exists(file.path) and file.size > limit:
		raise ValidationError('Размер файла превышает лимит %s Мб. Рекомендуемый размер фото 1500x1024 пикс.' % (limit/(1024*1024)))



""" Return True if the request comes from a mobile device """
def IsMobile(request):
	import re

	MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

	if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
		return True
	else:
		return False



def update_google_sitemap():
	try:
		ping_google() #сообщим Google о изменениях в sitemap.xml
	except Exception:
		pass


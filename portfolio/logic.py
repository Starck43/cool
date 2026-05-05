from io import BytesIO
from os import path, remove

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadhandler import MemoryFileUploadHandler
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail
from uuslug import slugify
from PIL import Image, ImageOps

IMAGE_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'}
ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}  # Форматы для сохранения

DEFAULT_SIZE = getattr(settings, 'DJANGORESIZED_DEFAULT_SIZE', [1500, 1024])
DEFAULT_QUALITY = getattr(settings, 'DJANGORESIZED_DEFAULT_QUALITY', 85)
DEFAULT_KEEP_META = getattr(settings, 'DJANGORESIZED_DEFAULT_KEEP_META', False)
THUMBNAIL_SIZE = getattr(settings, 'DJANGORESIZED_THUMBNAIL_SIZE', [300, 300])
OUTPUT_FORMAT = getattr(settings, 'DJANGORESIZED_OUTPUT_FORMAT', 'JPEG')


class MediaFileStorage(FileSystemStorage):
	def __init__(self, **kwargs):
		self.output_name = kwargs.get('output', None)
		super().__init__()

	def get_available_name(self, name, max_length=None):
		if self.output_name:
			name = self.output_name
		else:
			upload_folder, filename = path.split(name)
			if upload_folder:
				upload_folder += '/'
			# print(upload_folder, filename)
			filename, ext = path.splitext(filename)
			name = upload_folder + slugify(filename) + ext

		if path.exists(self.path(name)):  # если такой файл есть на диске, то удалим его
			remove(self.path(name))

		return name


class ImageUploadHandler(MemoryFileUploadHandler):
	""" Обработчик загрузки изображений с оптимизацией """

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._image_processed = False

	def _should_process_image(self, img: Image.Image) -> bool:
		"""Определяет, нужно ли обрабатывать изображение"""
		# Проверяем размер
		if img.width > DEFAULT_SIZE[0] or img.height > DEFAULT_SIZE[1]:
			return True

		# Проверяем тип
		if OUTPUT_FORMAT != 'JPEG' and self.content_type != f'image/{OUTPUT_FORMAT.lower()}':
			return True

		# Специальные поля
		if self.field_name in ['logo', 'map_thumb']:
			return True

		return False

	def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
		"""Конвертирует изображение в RGB с правильной обработкой альфа-канала"""
		if img.mode == 'RGB':
			return img

		if img.mode in ('RGBA', 'LA', 'P'):
			# Создаем белый фон
			background = Image.new('RGB', img.size, (255, 255, 255))
			if img.mode == 'P':
				img = img.convert('RGBA')

			# Вставляем изображение с учетом прозрачности
			if img.mode == 'RGBA':
				background.paste(img, mask=img.split()[-1])
			else:
				background.paste(img)
			return background

		# Для остальных режимов просто конвертируем
		return img.convert('RGB')

	def _optimize_image(self, img: Image.Image) -> BytesIO:
		output = BytesIO()

		# Определяем целевой размер
		target_size = THUMBNAIL_SIZE if self.field_name in ['logo', 'map_thumb'] else DEFAULT_SIZE

		# Вычисляем новые размеры с сохранением пропорций
		img.thumbnail(target_size, Image.Resampling.LANCZOS)

		# Конвертируем в RGB если нужно для JPEG/WEBP
		if OUTPUT_FORMAT in ('JPEG', 'WEBP'):
			img = self._convert_to_rgb(img)

		# Настройки сохранения
		save_kwargs = {
			'format': OUTPUT_FORMAT,
			'quality': DEFAULT_QUALITY,
			'optimize': True,
		}

		# Прогрессивный JPEG для лучшего UX
		if OUTPUT_FORMAT == 'JPEG':
			save_kwargs['progressive'] = True
			save_kwargs['quality'] = DEFAULT_QUALITY

		# Для WEBP дополнительные настройки
		if OUTPUT_FORMAT == 'WEBP':
			save_kwargs['method'] = 6  # Медленнее, но лучше сжатие
			save_kwargs['quality'] = DEFAULT_QUALITY

		# Сохраняем метаданные
		if DEFAULT_KEEP_META and hasattr(img, 'info'):
			# Безопасно копируем только нужные метаданные
			info = img.info.copy()
			# Удаляем потенциально проблемные данные
			info.pop('exif', None)
			info.pop('progression', None)
			# Для некоторых форматов
			if OUTPUT_FORMAT == 'JPEG' and 'exif' in info:
				save_kwargs['exif'] = info['exif']

		img.save(output, **save_kwargs)
		output.seek(0)

		return output

	def file_complete(self, file_size: int):
		"""Обработка завершения загрузки файла"""
		# Проверяем, нужно ли обрабатывать
		if self.content_type not in IMAGE_CONTENT_TYPES:
			return super().file_complete(file_size)

		try:
			self.file.seek(0)

			with Image.open(self.file) as img:
				if self._should_process_image(img):
					# Оптимизируем изображение
					optimized = self._optimize_image(img)

					# Обновляем данные файла
					self.file = optimized
					self.content_type = f'image/{OUTPUT_FORMAT.lower()}'

					# Меняем расширение
					name_without_ext = path.splitext(self.file_name)[0]
					self.file_name = f'{name_without_ext}.{OUTPUT_FORMAT.lower()}'

					self._image_processed = True
					optimized.seek(0)

		except Exception as e:
			import logging
			logging.error(f"Image optimization failed for {self.file_name}: {e}", exc_info=True)
		# В случае ошибки возвращаем исходный файл

		return super().file_complete(file_size)


def portfolio_upload_to(instance, filename):
	""" portfolio files will be uploaded to MEDIA_ROOT/uploads/<porfolio>/<filename> """
	return '{0}{1}/{2}'.format(settings.FILES_UPLOAD_FOLDER, instance.portfolio.slug, filename)


def get_image_html(obj):
	if obj and path.isfile(path.join(settings.MEDIA_ROOT, obj.name)):
		size = '%sx%s' % (settings.ADMIN_THUMBNAIL_SIZE[0], settings.ADMIN_THUMBNAIL_SIZE[1])
		thumb = get_thumbnail(obj.name, size, quality=settings.ADMIN_THUMBNAIL_QUALITY)
		return format_html('<img src="{0}" width="50"/>', thumb.url)
	else:
		return format_html('<img src="/media/no-image.png" width="50"/>')


def limit_file_size(file):
	""" Image file size validator """
	limit = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
	if path.exists(file.path) and file.size > limit:
		raise ValidationError(
			'Размер файла превышает лимит %s Мб. Рекомендуемый размер фото 1500x1024 пикс.' % (limit / (1024 * 1024)))


def clear_cache(key='default'):  # `default` is a key from CACHES dict in settings.py
	""" Clear cache function """
	from django.core.cache import cache
	cache_page = cache
	if cache_page:
		cache_page.clear()
	return cache_page


def is_mobile(request):
	""" Return True if the request comes from a mobile device """
	import re

	mobile_agent_re = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

	if mobile_agent_re.match(request.META['HTTP_USER_AGENT']):
		return True
	else:
		return False

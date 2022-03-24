import re
from os import path, rename, rmdir, listdir
from datetime import date

from django.core.validators import RegexValidator
from django.conf import settings
from django.utils.text import slugify
from django.utils.html import format_html
from django.db import models
#from django.db.models import Q

from sorl.thumbnail import delete
from uuslug import uuslug

from .logic import MediaFileStorage, PortfolioUploadTo, get_image_html, limit_file_size



class Service(models.Model):
	title = models.CharField('Название услуги', max_length=50, help_text='')
	description = models.TextField('Краткая информация', blank=True, help_text='Краткое описание для вывода в разделе на главной странице')
	slug = models.SlugField('Ярлык', max_length=50, unique=True, help_text='Имя раздела (лат.) для использования в качестве внутренней ссылки для выбора группы Портфолио')
	cover = models.ImageField('Фото в шапке', blank=True, upload_to='covers/', storage=MediaFileStorage(), validators=[limit_file_size], help_text='Фото для слайдера в шапке на главной странице. Размер файла не более %s Мб' % round(settings.FILE_UPLOAD_MAX_MEMORY_SIZE/1024/1024))

	seo_title = models.CharField('Заголовок страницы', max_length=150, blank=True,help_text='Заголовок для выдачи в поисковой системе')
	seo_description = models.TextField('Мета описание', max_length=255, blank=True, help_text='Описание записи в поисковой выдаче. Рекомендуется 70-80 символов')
	seo_keywords = models.CharField('Ключевые слова', max_length=255, blank=True, help_text='Укажите через запятую поисковые словосочетания, которые присутствуют в заголовке или описании самой записи. Рекомендуется до 20 слов и не более 3-х повторов')

	class Meta:
		db_table = "services"
		ordering = ['title']
		verbose_name = 'Услуга'
		verbose_name_plural = 'Услуги'

	def save(self, *args, **kwargs):
		if self.title and not self.seo_title:
			self.seo_title = self.title

		if self.description and not self.seo_description:
			self.seo_description = self.description

		super().save(*args, **kwargs)


	def __str__(self):
		return self.title



class Portfolio(models.Model):
	service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio', verbose_name = 'Раздел')
	title = models.CharField('Заголовок', max_length=50, blank=True, help_text='Заголовок')
	slug = models.SlugField('Ярлык', max_length=50, unique=True, blank=True, help_text='Заголовок на латинском языке для формирования красивого адреса. Оставьте пустым для автоматического формирования')
	excerpt = models.TextField('Краткое описание', blank=True, help_text='Для вывода под заголовком у портфолио')
	created = models.DateField('Дата создания', blank=True, default=date.today, help_text='Укажите для себя дату создания портфолио, чтобы знать что заменить со временем')

	class Meta:
		ordering = ['-created', 'slug']
		verbose_name = 'Портфолио'
		verbose_name_plural = 'Портфолио'


	def save(self, *args, **kwargs):
		if not self.slug:
			if not self.title:
				if self.pk:
					last_id = self.pk
				else:
					last_id = Portfolio.objects.latest('id').id
					if last_id:
						last_id += 1
					else:
						last_id = 1
				self.slug = f'portfolio-{last_id}'
			else:
				self.slug = uuslug(self.title.lower(), instance=self)
		super().save(*args, **kwargs)


	def __str__(self):
		return self.title if self.title else f'Портфолио-{self.pk}'



class Image(models.Model):
	portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True, related_name='images', verbose_name = 'Портфолио')
	title = models.CharField('Заголовок', max_length=100, blank=True)
	excerpt = models.TextField('Описание', blank=True, help_text='Описание фото доступно только в просмотрщике')
	file = models.ImageField('Файл', upload_to=PortfolioUploadTo, storage=MediaFileStorage(), validators=[limit_file_size], help_text='Размер файла не более %s Мб' % round(settings.FILE_UPLOAD_MAX_MEMORY_SIZE/1024/1024))
	general = models.BooleanField('Главное фото', default=False, help_text='Главное фото крупным планом в портфолио')

	# Metadata
	class Meta:
		verbose_name = 'Фото'
		verbose_name_plural = 'Фото'
		ordering = ['portfolio','-general']
		db_table = 'images'


	def __str__(self):
		return self.title if self.title else '<Без имени>'


	def file_thumb(self):
		return get_image_html(self.file)
	file_thumb.short_description = 'Фото'


	def filename(self):
		return self.file.name.rsplit('/', 1)[-1]
	filename.short_description = 'Имя файла'


	def delete(self, *args, **kwargs):
		# физически удалим файл с диска, если он единственный
		delete(self.file)
		folder = path.join(settings.MEDIA_ROOT, path.dirname(self.file.name))
		if not listdir(folder): # если пустая папка, то удалим и ее
			rmdir(folder)

		super().delete(*args, **kwargs)



class Contact(models.Model):
	phone_regex = RegexValidator(regex=r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', message="Допустимы цифры, знак плюс, символы пробела и круглые скобки")

	logo = models.ImageField('Логотип', blank=True, storage=MediaFileStorage(output='logo.jpg'), help_text='Изобоажение логотипа в заголовке и подвале сайта')
	title = models.CharField('Подпись', max_length=255, blank=True, help_text='Текст, который будет отображаться в заголовке с логотипом')
	name = models.CharField('Название компании(владелец)', max_length=100)
	description = models.TextField('О себе', blank=True, help_text='Краткое описание своей деятельности. Текст добавляется на главную страницу')

	address = models.CharField('Адрес', max_length=100, blank=True)
	phone = models.CharField('Контактный телефон', validators=[phone_regex], max_length=18, blank=True)
	email = models.EmailField('E-mail', max_length=75, blank=True)
	vk = models.CharField('Вконтакте', max_length=75, blank=True, default="https://vk.com")
	telegram = models.CharField('Телеграм', max_length=75, blank=True, default="https://t.me")
	instagram = models.CharField('Instagram', max_length=75, blank=True, default="https://instagram.com")
	map_thumb = models.ImageField('Карта', blank=True, storage=MediaFileStorage(output='map.jpg'), help_text='Изображение карты местности для отображения в блоке контактов. Фото не менее 300px по ширине')
	map_url = models.CharField('Адрес на карте', max_length=255, blank=True, default='https://yandex.ru/maps/?text=', help_text='Ссылка для перехода на карту Yandex')

	seo_title = models.CharField('Заголовок для главной страницы', max_length=150, blank=True,help_text='Заголовок для выдачи в поисковой системе')
	seo_description = models.TextField('Мета описание для главной страницы', max_length=255, blank=True, help_text='Описание записи в поисковой выдаче. Рекомендуется 70-80 символов')
	seo_keywords = models.CharField('Ключевые слова для главной страницы', max_length=255, blank=True, help_text='Укажите через запятую поисковые словосочетания, которые присутствуют в заголовке или описании самой записи. Рекомендуется до 20 слов и не более 3-х повторов')

	# Metadata
	class Meta:
		verbose_name = 'Контакт'
		verbose_name_plural = 'Контакты'


	def save(self, *args, **kwargs):
		if self.title and not self.seo_title:
			self.seo_title = self.title

		if self.description and not self.seo_description:
			self.seo_description = self.description

		mapUrl = self._meta.get_field('map_url').default
		if self.map_url and not re.match(r'^https?:\/\/|\/$', self.map_url):
			self.map_url = mapUrl+self.map_url

		super().save(*args, **kwargs)


	def __str__(self):
		return self.name


	def file_thumb(self):
		return get_image_html(self.logo)
	file_thumb.short_description = 'Логотип'


	def __iter__(self):
		for field in self._meta.fields:
			label = field.verbose_name
			name = field.name
			value = field.value_to_string(self)

			if value and name in ['address', 'phone','email','vk','telegram','instagram']:
				link = None
				field_type = 'social' if name in ['vk','telegram','instagram'] else 'contact'

				if name in ['phone','email'] :
					prefix = 'tel' if name == 'phone' else 'mailto'
					link = prefix+':'+value.lower()

				if type(field.default) is str and field.default != value:
					link = field.default+'/'+value.lower().rsplit('/', 1)[-1]
					link = 'https://'+re.sub(r'^https?:\/\/|\/$', '', link, flags=re.MULTILINE)

				yield (name, label, value, link, field_type)



from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from portfolio.models import Portfolio


class StaticViewSitemap(Sitemap):
	priority = 0.5          # Приоритет
	changefreq = 'daily'   # Частота проверки

	def items(self):
		return [
			'index',
			# 'contacts-url',
			'portfolio:portfolio-list-url',
		]

	def location(self, item):
		return reverse(item)


# class PortfolioSitemap(Sitemap):
	priority = 1
	changefreq = 'daily'
	def items(self):
		return Portfolio.objects.all()

sitemaps = {
	'static': StaticViewSitemap,
	'portfolio': PortfolioSitemap,
}


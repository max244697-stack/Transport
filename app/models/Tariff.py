from django.db import models

from app.models.Category import Category


class Tariff(models.Model):
	category = models.ForeignKey(
		Category,
		related_name='tariffs',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		verbose_name='Категорія',
	)
	price = models.CharField(max_length=100, verbose_name='Ціна')
	description = models.TextField(blank=True, verbose_name='Опис')
	order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
	is_featured = models.BooleanField(default=False, verbose_name='Виділити')

	class Meta:
		db_table = 'tariffs'
		ordering = ('order', 'pk')
		verbose_name = 'Тариф'
		verbose_name_plural = 'Тарифи'

	def __str__(self):
		category_name = self.category.name if self.category_id else 'Без категорії'
		return f'{category_name}: {self.price}'

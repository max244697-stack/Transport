from django.db import models


class CompletedOrder(models.Model):
	image = models.ImageField(upload_to='completed_orders/', verbose_name='Фото')
	description = models.TextField(blank=True, verbose_name='Опис')
	order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
	is_published = models.BooleanField(default=True, verbose_name='Показувати на сайті')

	class Meta:
		db_table = 'completed_orders'
		ordering = ('order', 'pk')
		verbose_name = 'Виконане замовлення'
		verbose_name_plural = 'Виконані замовлення'

	def __str__(self):
		return f'Фото #{self.pk}'

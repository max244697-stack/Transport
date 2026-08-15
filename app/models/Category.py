from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=150, unique=True, verbose_name='Назва')
	order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

	class Meta:
		db_table = 'categories'
		ordering = ('order', 'pk')
		verbose_name = 'Категорія'
		verbose_name_plural = 'Категорії'

	def __str__(self):
		return self.name

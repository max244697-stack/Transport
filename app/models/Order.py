from django.db import models


class Order(models.Model):
	namber = models.CharField(max_length=150, verbose_name='Номер')
	type = models.CharField(max_length=100, verbose_name='Тип')
	adress_from = models.TextField(blank=True, verbose_name='Звідки')
	adress_to = models.TextField(blank=True, verbose_name='Куди')
	scheduled_date = models.DateField(null=True, blank=True, verbose_name='Бажана дата')
	scheduled_time = models.TimeField(null=True, blank=True, verbose_name='Орієнтовний час')
	date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
	order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
	is_featured = models.BooleanField(default=False, verbose_name='Виділити')

	class Meta:
		db_table = 'orders'
		ordering = ('order', 'pk')
		verbose_name = 'Замовлення'
		verbose_name_plural = 'Замовлення'

	def __str__(self):
		return f"{self.namber or 'Без номера'} — {self.type or 'Без типу'}"

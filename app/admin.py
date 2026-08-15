from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from app.models.Category import Category
from app.models.CompletedOrder import CompletedOrder
from app.models.Order import Order
from app.models.Tariff import Tariff

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'order')
	list_editable = ('order',)
	search_fields = ('name',)
	ordering = ('order', 'pk')
	fieldsets = (
		(None, {
			'fields': ('name',),
		}),
		('Відображення', {
			'fields': ('order',),
		}),
	)

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
	list_display = ('category', 'price', 'order', 'is_featured')
	list_editable = ('order', 'is_featured')
	list_filter = ('category', 'is_featured')
	search_fields = ('price', 'description', 'category__name')
	ordering = ('order', 'pk')
	fieldsets = (
		(None, {
			'fields': ('category', 'price', 'description'),
		}),
		('Відображення', {
			'fields': ('order', 'is_featured'),
		}),
	)


@admin.register(CompletedOrder)
class CompletedOrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'image_preview', 'order', 'is_published')
	list_editable = ('order', 'is_published')
	list_filter = ('is_published',)
	search_fields = ('description',)
	ordering = ('order', 'pk')
	readonly_fields = ('image_preview',)
	fieldsets = (
		(None, {
			'fields': ('image', 'image_preview', 'description'),
		}),
		('Відображення', {
			'fields': ('order', 'is_published'),
		}),
	)

	@admin.display(description='Превʼю')
	def image_preview(self, obj):
		if obj.image:
			return format_html(
				'<img src="{}" style="max-height: 60px; border-radius: 4px;" />',
				obj.image.url,
			)
		return '—'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'namber', 'type', 'scheduled_date', 'scheduled_time', 'adress_from', 'adress_to', 'date', 'order', 'is_featured')
	list_editable = ('order', 'is_featured')
	list_filter = ('is_featured', 'scheduled_date', 'date')
	search_fields = ('namber', 'type', 'adress_from', 'adress_to')
	ordering = ('-date', 'order', 'pk')
	fieldsets = (
		(None, {
			'fields': ('namber', 'type', 'scheduled_date', 'scheduled_time', 'adress_from', 'adress_to', 'date'),
		}),
		('Відображення', {
			'fields': ('order', 'is_featured'),
		}),
	)
	readonly_fields = ('date',)

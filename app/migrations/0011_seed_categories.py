from django.db import migrations


CATEGORIES = [
    'Квартирний переїзд',
    'Офісний переїзд',
    'Перевезення меблів',
    'Доставка техніки',
    'Будматеріали',
    'Інше',
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('app', 'Category')
    for index, name in enumerate(CATEGORIES):
        Category.objects.get_or_create(
            name=name,
            defaults={'order': index},
        )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('app', 'Category')
    Category.objects.filter(name__in=CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_category_remove_tariff_name_tariff_category'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]

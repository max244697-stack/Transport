from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_category_options_alter_category_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='need_loaders',
            field=models.BooleanField(default=False, verbose_name='Потрібні вантажники'),
        ),
    ]

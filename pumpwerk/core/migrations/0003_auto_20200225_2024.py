# Generated by Django 2.2.6 on 2020-02-25 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_setting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='terra_daily_rate',
            field=models.DecimalField(decimal_places=2, default=6.0, max_digits=8),
        ),
    ]

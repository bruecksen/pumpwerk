# Generated by Django 2.2.10 on 2020-02-27 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0007_auto_20200227_1036'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='total_food',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='bill',
            name='total_invest',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='bill',
            name='total_luxury',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]

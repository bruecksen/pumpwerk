# Generated by Django 2.2.11 on 2020-04-07 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0023_auto_20200407_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbill',
            name='attendance_days',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Attend. days'),
        ),
    ]

# Generated by Django 2.2.10 on 2020-03-03 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0013_remove_userbill_expense_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbill',
            name='attendance_days',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]

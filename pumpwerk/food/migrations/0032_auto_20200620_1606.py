# Generated by Django 2.2.11 on 2020-06-20 14:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0031_auto_20200620_1552'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='inventory_food_sum',
            new_name='additional_inventory_food',
        ),
    ]
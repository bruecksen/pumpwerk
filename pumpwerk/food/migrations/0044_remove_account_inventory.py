# Generated by Django 2.2.11 on 2020-10-08 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0043_inventory_inventory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='inventory',
        ),
    ]
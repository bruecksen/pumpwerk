# Generated by Django 2.2.11 on 2020-06-20 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0030_auto_20200620_1527'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='name',
            new_name='title',
        ),
        migrations.AlterField(
            model_name='inventory',
            name='bills',
            field=models.ManyToManyField(blank=True, to='food.Bill'),
        ),
    ]
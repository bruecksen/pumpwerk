# Generated by Django 2.2.6 on 2020-02-25 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bill',
            old_name='users',
            new_name='members',
        ),
        migrations.AlterField(
            model_name='bill',
            name='year',
            field=models.PositiveIntegerField(default=2020),
        ),
    ]

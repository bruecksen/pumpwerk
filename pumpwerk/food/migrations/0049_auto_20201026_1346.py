# Generated by Django 2.2.11 on 2020-10-26 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0048_auto_20201008_1400'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='is_notified',
        ),
        migrations.AddField(
            model_name='bill',
            name='overview',
            field=models.TextField(blank=True, null=True),
        ),
    ]
# Generated by Django 2.2.26 on 2022-02-13 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0052_auto_20210207_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='terrainvoice',
            name='fee',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Additional fee'),
        ),
    ]
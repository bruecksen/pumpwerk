# Generated by Django 2.2.26 on 2022-02-25 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0056_auto_20220225_1039'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='terra_food_pumpwerk_fee_sum',
            new_name='terra_food_pumpwerk_fee',
        ),
    ]
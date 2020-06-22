# Generated by Django 2.2.11 on 2020-06-22 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0038_auto_20200621_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpayback',
            name='total_days',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='terra_deposit_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Deposit sum'),
        ),
    ]

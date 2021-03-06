# Generated by Django 2.2.11 on 2020-10-08 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0046_auto_20201008_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_account', to='food.Inventory'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='account_inventory', to='food.Account'),
        ),
    ]

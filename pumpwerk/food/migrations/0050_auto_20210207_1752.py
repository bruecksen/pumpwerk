# Generated by Django 2.2.11 on 2021-02-07 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0049_auto_20201026_1346'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='account_carry_over',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='food.Account'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='sum_inventory',
            field=models.DecimalField(decimal_places=2, help_text='incl. luxury', max_digits=8),
        ),
    ]
# Generated by Django 2.2.11 on 2020-06-19 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0026_auto_20200512_1511'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventory',
            options={'ordering': ['-year', '-month'], 'verbose_name': 'Inventory', 'verbose_name_plural': 'Inventories'},
        ),
        migrations.AlterModelOptions(
            name='terrainvoice',
            options={'ordering': ['-date'], 'verbose_name': 'Terra Invoice', 'verbose_name_plural': 'Terra Invoices'},
        ),
        migrations.AddField(
            model_name='terrainvoice',
            name='is_pumpwerk',
            field=models.BooleanField(default=True),
        ),
    ]
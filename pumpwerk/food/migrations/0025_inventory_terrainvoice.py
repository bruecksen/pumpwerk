# Generated by Django 2.2.11 on 2020-05-12 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0024_auto_20200407_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='TerraInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('invoice_number', models.CharField(blank=True, max_length=255, null=True)),
                ('invoice_sum', models.DecimalField(decimal_places=2, max_digits=8)),
                ('deposit', models.DecimalField(decimal_places=2, max_digits=8)),
                ('luxury_sum', models.DecimalField(decimal_places=2, max_digits=8)),
                ('other_sum', models.DecimalField(decimal_places=2, default=0, help_text='Other extraordinary sum wich should not be included in the terra factor.', max_digits=8)),
            ],
            options={
                'verbose_name': 'Terra Invoice',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.PositiveSmallIntegerField(choices=[(1, 'Januar'), (2, 'Februar'), (3, 'März'), (4, 'April'), (5, 'Mai'), (6, 'Juni'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'December')])),
                ('year', models.PositiveIntegerField(default=2020)),
                ('sum_inventory', models.DecimalField(decimal_places=2, max_digits=8)),
                ('sum_cash', models.DecimalField(decimal_places=2, max_digits=8)),
                ('comment', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Inventory',
                'ordering': ['-year', '-month'],
                'unique_together': {('month', 'year')},
            },
        ),
    ]

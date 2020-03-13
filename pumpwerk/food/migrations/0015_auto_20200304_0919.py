# Generated by Django 2.2.10 on 2020-03-04 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0014_auto_20200303_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbill',
            name='expense_types',
            field=models.ManyToManyField(to='food.ExpenseType'),
        ),
        migrations.AlterField(
            model_name='userbill',
            name='credit',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True),
        ),
    ]
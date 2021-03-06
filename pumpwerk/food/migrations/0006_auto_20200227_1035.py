# Generated by Django 2.2.10 on 2020-02-27 10:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('food', '0005_userbill_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bill',
            options={'ordering': ['-year', '-month'], 'verbose_name': 'Bill'},
        ),
        migrations.AlterModelOptions(
            name='expense',
            options={'verbose_name': 'Expense'},
        ),
        migrations.AlterModelOptions(
            name='expensetype',
            options={'verbose_name': 'Expense Type'},
        ),
        migrations.AlterModelOptions(
            name='userbill',
            options={'ordering': ['-bill__year', '-bill__month'], 'verbose_name': 'User Bill'},
        ),
        migrations.AddField(
            model_name='userbill',
            name='carry_over',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='userbill',
            name='luxury_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='userbill',
            unique_together={('bill', 'user')},
        ),
    ]

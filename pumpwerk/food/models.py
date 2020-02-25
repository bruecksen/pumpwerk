from calendar import monthrange
from datetime import date

from django.db import models
from django.utils.dates import MONTHS
from django.conf import settings


class Bill(models.Model):
    month = models.PositiveSmallIntegerField(choices=MONTHS.items())
    year = models.PositiveIntegerField(default=date.today().year)
    days_in_month = models.PositiveIntegerField(editable=False)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)
    terra_daily_rate = models.DecimalField(max_digits=8, decimal_places=2)


    class Meta:
        unique_together = ['month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return "%s %s" % (MONTHS[self.month], self.year)

    def save(self, *args, **kwargs):
        self.days_in_month = monthrange(self.year, self.month)[1]
        super(Bill, self).save(*args, **kwargs)
    

class UserBill(models.Model):
    bill = models.ForeignKey('Bill', on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    attendance_days = models.PositiveIntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    has_payed = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)

    class Meta:
        unique_together = ['bill', 'user']
        ordering = ['-bill__year', '-bill__month']

    def __str__(self):
        return "%s - %s" % (self.bill, self.user)


class ExpenseType(models.Model):
    name = models.CharField(max_length=255)
    is_invest = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Expense(models.Model):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    user_bill = models.ForeignKey(UserBill, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=8, decimal_places=2)




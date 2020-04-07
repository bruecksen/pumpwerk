from calendar import monthrange
from datetime import date

from django.db.models import Sum
from django.db.models import F
from django.db import models
from django.conf import settings


MONTHS = {
    1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
    7: 'July', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November',
    12: 'December'
}


class Bill(models.Model):
    month = models.PositiveSmallIntegerField(choices=MONTHS.items())
    year = models.PositiveIntegerField(default=date.today().year)
    days_in_month = models.PositiveIntegerField(editable=False, verbose_name='Days/Mo')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)
    expense_types = models.ManyToManyField('ExpenseType')
    terra_daily_rate = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Terra Rate')
    total_attendance_days = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Total Days')
    total_supermarket = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_invest = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_terra = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_luxury = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_notified = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)


    class Meta:
        unique_together = ['month', 'year']
        ordering = ['-year', '-month']
        verbose_name = 'Bill'

    def __str__(self):
        return "%s %s" % (self.get_month(), self.year)

    def save(self, *args, **kwargs):
        self.days_in_month = monthrange(self.year, self.month)[1]
        super(Bill, self).save(*args, **kwargs)

    def get_month(self):
        return MONTHS[self.month]

    def make_bill_calculation(self):
        user_bills = self.userbill_set.all()
        # calculate totals of month and save in object
        total_attendance_days = user_bills.aggregate(total_attendance_days=Sum(F('attendance_days') * F('calculation_factor')))['total_attendance_days']
        total_luxury = user_bills.aggregate(Sum('luxury_sum'))['luxury_sum__sum'] or 0

        food_expense_types = ExpenseType.objects.filter(is_invest=False)
        invest_expense_types = ExpenseType.objects.filter(is_invest=True)

        all_food_expenses = Expense.objects.filter(expense_type__in=food_expense_types, user_bill__bill=self)
        total_supermarket = all_food_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        all_invest_expenses = Expense.objects.filter(expense_type__in=invest_expense_types, user_bill__bill=self)
        total_invest = all_invest_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        self.total_attendance_days = total_attendance_days
        self.total_supermarket = total_supermarket
        self.total_terra = total_attendance_days * self.terra_daily_rate
        self.total_invest = total_invest
        self.total_luxury = total_luxury
        self.daily_rate = (self.total_supermarket + self.total_terra) / self.total_attendance_days
        self.save()

        # calculate the share per user for the invest sum, respecting the calculation rate
        invest_share = self.total_invest / user_bills.filter(expense_types__in=invest_expense_types).aggregate(user_count=Sum('calculation_factor'))['user_count']
        # calculate user Food sum
        for user_bill in user_bills:
            user_bill.food_sum = user_bill.calculation_factor * user_bill.attendance_days * user_bill.bill.daily_rate
            if user_bill.expense_types.filter(is_invest=True).exists():
                user_bill.invest_sum = invest_share * user_bill.calculation_factor
            else:
                user_bill.invest_sum = 0
            user_expense_food = all_food_expenses.filter(user_bill=user_bill).aggregate(Sum('amount'))['amount__sum'] or 0
            user_expense_invest = all_invest_expenses.filter(user_bill=user_bill).aggregate(Sum('amount'))['amount__sum'] or 0
            user_bill.total = user_bill.credit + user_expense_food + user_expense_invest - user_bill.food_sum - user_bill.invest_sum - user_bill.luxury_sum
            user_bill.expense_sum = user_expense_food + user_expense_invest
            user_bill.save()


class UserBill(models.Model):
    bill = models.ForeignKey('Bill', on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    calculation_factor = models.DecimalField(max_digits=8, decimal_places=2, default=1, verbose_name='Calcf.')
    expense_types = models.ManyToManyField('ExpenseType')
    attendance_days = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Attend. days')
    credit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    food_sum = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    luxury_sum = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    invest_sum = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    expense_sum = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    has_payed = models.BooleanField(default=False, verbose_name='Payed?')
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['bill', 'user']
        ordering = ['-bill__year', '-bill__month']
        verbose_name = 'User Bill'

    def __str__(self):
        return "%s - %s" % (self.bill, self.user)


class ExpenseType(models.Model):
    name = models.CharField(max_length=255)
    is_invest = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Expense Type'

    def __str__(self):
        return self.name


class Expense(models.Model):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    user_bill = models.ForeignKey(UserBill, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Expense'




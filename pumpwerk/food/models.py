from calendar import monthrange
from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import F, Sum

MONTHS = {
    1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
    7: 'July', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November',
    12: 'December'
}


class Bill(models.Model):
    bill_date = models.DateField(blank=True, null=True)
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
        ordering = ['-bill_date']
        verbose_name = 'Bill'

    def __str__(self):
        return "Bill {}".format(self.bill_date)

    def save(self, *args, **kwargs):
        self.days_in_month = monthrange(self.bill_date.year, self.bill_date.month)[1]
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
    has_paid = models.BooleanField(default=False, verbose_name='Paid?')
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['bill', 'user']
        ordering = ['-bill__bill_date']
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


class Inventory(models.Model):
    inventory_date = models.DateField(default=date.today)
    sum_inventory = models.DecimalField(max_digits=8, decimal_places=2)
    sum_cash = models.DecimalField(max_digits=8, decimal_places=2)
    sum_luxury = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    bills = models.ManyToManyField('Bill', blank=True)

    class Meta:
        ordering = ['-inventory_date']
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return "Inventory: {}".format(self.inventory_date)

    def get_previous_inventory(self):
        return Inventory.objects.filter(inventory_date__lt=self.inventory_date).first()


class TerraInvoice(models.Model):
    terra_invoice_date = models.DateField()
    invoice_number = models.CharField(max_length=255, blank=True, null=True)
    invoice_sum = models.DecimalField(max_digits=8, decimal_places=2)
    deposit_sum = models.DecimalField(max_digits=8, decimal_places=2)
    luxury_sum = models.DecimalField(max_digits=8, decimal_places=2)
    other_sum = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Other extraordinary sum wich should not be included in the terra factor.")
    is_pumpwerk = models.BooleanField(default=True, verbose_name='Is pumpwerk order?')

    class Meta:
        verbose_name = 'Terra Invoice'
        verbose_name_plural = 'Terra Invoices'
        ordering = ['-terra_invoice_date']

    def __str__(self):
        return "Terra Invoice: {} {}".format(self.invoice_number, self.terra_invoice_date)


class Payment(models.Model):
    title = models.CharField(max_length=255)
    payment_date = models.DateField(default=date.today)
    payment_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    bills = models.ManyToManyField('TerraInvoice')

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return "Payment: {}".format(self.when)


class Account(models.Model):
    title = models.CharField(max_length=255)
    inventory = models.OneToOneField('Inventory', on_delete=models.PROTECT)
    additional_inventory_food = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Add. inv. food')
    terra_luxury_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    luxury_consumed = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    luxury_paid_diff = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Lux paid diff')
    terra_brutto_all_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Sum of all brutto terra invoice totals", verbose_name='Tot. Terra brutto (all)')
    terra_food_others_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Tot. food (others)')
    terra_brutto_others_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Sum of all terra invoices without deposit and not from pumpwerk")
    terra_deposit_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Deposit bal.')
    terra_food_pumpwerk_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    food_expenses_pumpwerk_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Tot. food (PW)')
    attendance_day_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Tot. days')
    corrected_terra_daily_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='New Terra rate')
    
    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-inventory__created']

    def __str__(self):
        return "Account: {}".format(self.title)

    def calculate(self):
        previous_inventory = self.inventory.get_previous_inventory()
        self.additional_inventory_food = (self.inventory.sum_inventory - self.inventory.sum_luxury) - (previous_inventory.sum_inventory - previous_inventory.sum_luxury)
        
        user_bills = UserBill.objects.filter(bill__in=self.inventory.bills.all())
        self.attendance_day_sum = user_bills.aggregate(attendance_days_sum=Sum('attendance_days'))['attendance_days_sum']
        user_bill_luxury_sum = user_bills.aggregate(luxury_sum=Sum('luxury_sum'))['luxury_sum']
        
        terra_invoices = TerraInvoice.objects.filter(terra_invoice_date__gt=previous_inventory.inventory_date, terra_invoice_date__lte=self.inventory.inventory_date)
        terra_sums = terra_invoices.aggregate(invoice_sum=Sum('invoice_sum'), deposit_sum=Sum('deposit_sum'), luxury_sum=Sum('luxury_sum'), other_sum=Sum('other_sum'))
        self.terra_luxury_sum = terra_sums['luxury_sum']
        self.luxury_consumed = self.terra_luxury_sum - (self.inventory.sum_luxury - previous_inventory.sum_luxury)
        self.luxury_paid_diff = user_bill_luxury_sum - self.luxury_consumed - self.inventory.sum_cash
        self.terra_brutto_all_sum = terra_sums['invoice_sum']
        self.terra_deposit_sum = terra_sums['deposit_sum']
        terra_brutto_others_sum = terra_invoices.filter(is_pumpwerk=False).aggregate(invoice_sum=Sum('invoice_sum'))['invoice_sum']
        other_invoice_deposit_sum = terra_invoices.filter(is_pumpwerk=False).aggregate(deposit_sum=Sum('deposit_sum'))['deposit_sum']
        self.terra_food_others_sum = terra_brutto_others_sum - other_invoice_deposit_sum

        self.terra_brutto_others_sum = terra_brutto_others_sum

        self.terra_food_pumpwerk_sum = self.terra_brutto_all_sum - self.terra_food_others_sum - self.terra_luxury_sum - self.terra_deposit_sum
        self.food_expenses_pumpwerk_sum = self.terra_food_pumpwerk_sum - self.additional_inventory_food
        self.corrected_terra_daily_rate = self.food_expenses_pumpwerk_sum / self.attendance_day_sum
        self.save()


class UserPayback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    has_paid = models.BooleanField(default=False, verbose_name='Paid?')
    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'User payback'
        verbose_name_plural = 'User paybacks'
        ordering = ['-account__from_month', 'user']

    def __str__(self):
        return "User payback: {}".format(self.account.title)

from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.template.defaultfilters import date as date_filter
from django.conf import settings
from django.db import models
from django.db.models import F, Sum
from django.contrib.auth import get_user_model

MONTHS = {
    1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
    7: 'July', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November',
    12: 'December'
}

User = get_user_model()


class Bill(models.Model):
    bill_date = models.DateField(blank=True, null=True)
    days_in_month = models.PositiveIntegerField(editable=False, verbose_name='Days/Mo')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)
    expense_types = models.ManyToManyField('ExpenseType')
    terra_daily_rate = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Terra Rate')
    luxury_rate = models.DecimalField(max_digits=8, decimal_places=2, default=1, verbose_name='Luxury Rate', help_text="Preis pro Strich")
    total_attendance_days = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Total Days')
    total_supermarket = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_invest = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_terra = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_luxury = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    account_carry_over = models.OneToOneField('Account', blank=True, null=True, on_delete=models.SET_NULL)
    bill_carry_over = models.OneToOneField('Bill', blank=True, null=True, on_delete=models.SET_NULL)
    comment = models.TextField(blank=True, null=True)
    overview = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['-bill_date']
        verbose_name = 'Bill'

    def __str__(self):
        return "Bill {}".format(self.bill_date)

    def save(self, *args, **kwargs):
        self.days_in_month = monthrange(self.bill_date.year, self.bill_date.month)[1]
        super(Bill, self).save(*args, **kwargs)

    def generate_bill_overview(self):
        text = f"### Essensabrechnung: {date_filter(self.bill_date, 'F Y')} \n\n"
        text += f"Summe Anwesenheitstage: {self.total_attendance_days:.2f}\n"
        text += f"Summe Terra: {self.total_terra:.2f}€\n"
        text += f"Summe Supermarkt: {self.total_supermarket:.2f}€\n"
        text += f"Summe Invest: {self.total_invest:.2f}€\n"
        text += f"Tagessatz (Terra): {self.daily_rate:.2f} € ({self.terra_daily_rate:.2f}€)\n\n"
        text += "| Name | Tage | Bezahlen/Guthaben | Kredit + Ausgaben - Essen - Invest - Luxus |\n"
        text += "| :------------ |:---------------|:-----|:---------|\n"
        for user_bill in self.userbill_set.all().order_by('user__username'):
            text += f"| **{user_bill.user}** | {user_bill.attendance_days:.1f} | "
            if user_bill.get_user_has_to_pay_amount():
                text += f"Zu bezahlen: **{user_bill.get_user_has_to_pay_amount():.2f}€** | {user_bill.credit:.2f} + {user_bill.expense_sum:.2f} - {user_bill.food_sum:.2f} - {user_bill.invest_sum:.2f} - {user_bill.luxury_sum:.2f} |\n"
            elif user_bill.get_user_credit():
                text += f"Guthaben: {user_bill.get_user_credit():.2f}€ | {user_bill.credit:.2f} + {user_bill.expense_sum:.2f} - {user_bill.food_sum:.2f} - {user_bill.invest_sum:.2f} - {user_bill.luxury_sum:.2f} |\n"
        
        return text              


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
            user_credit = 0
            if self.account_carry_over and UserPayback.objects.filter(user=user_bill.user, account=self.account_carry_over).exists():
                # carry over positive and negative userpayback total
                user_credit += UserPayback.objects.get(user=user_bill.user, account=self.account_carry_over).total
            if self.bill_carry_over and UserBill.objects.filter(user=user_bill.user, bill=self.bill_carry_over).exists():
                last_user_bill = UserBill.objects.get(user=user_bill.user, bill=self.bill_carry_over)
                if last_user_bill.get_user_credit():
                    user_credit += last_user_bill.get_user_credit()
            user_bill.credit = user_credit
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
        self.overview = self.generate_bill_overview()
        self.save(update_fields=['overview'])


class UserBill(models.Model):
    bill = models.ForeignKey('Bill', on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    calculation_factor = models.DecimalField(max_digits=8, decimal_places=2, default=1, verbose_name='Calcf.')
    expense_types = models.ManyToManyField('ExpenseType')
    attendance_days = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Attend. days')
    credit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    food_sum = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    luxury_count = models.PositiveIntegerField(null=True, blank=True, help_text="Anzahl der Luxusstriche")
    luxury_sum = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0, verbose_name='Luxury')
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
    
    def save(self, *args, **kwargs):
        if self.luxury_count and not self.luxury_sum:
            self.luxury_sum = self.luxury_count * self.bill.luxury_rate
        super().save(*args, **kwargs)

    def get_user_has_to_pay_amount(self):
        return self.total <= 0 and abs(self.total) or None
    
    def get_user_credit(self):
        return self.total > 0 and abs(self.total) or None


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
    sum_inventory = models.DecimalField(max_digits=8, decimal_places=2, help_text="incl. luxury")
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
    luxury_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="(self.luxury_sum_7 * Decimal(1.07)) + (self.luxury_sum_19 * Decimal(1.19))")
    luxury_sum_7 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    luxury_sum_19 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    other_sum = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Other extraordinary sum wich should not be included in the terra factor.")
    is_pumpwerk = models.BooleanField(default=True, verbose_name='Is pumpwerk order?')
    fee = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Additional fee', default=1, help_text="Fee in percentage, e.g. 1 for 1% or 2 for 2%.")

    class Meta:
        verbose_name = 'Terra Invoice'
        verbose_name_plural = 'Terra Invoices'
        ordering = ['-terra_invoice_date']

    def __str__(self):
        return "Terra Invoice: {} {}".format(self.invoice_number, self.terra_invoice_date)

    def save(self, *args, **kwargs):
        if self.luxury_sum_7 or self.luxury_sum_19:
            self.luxury_sum = (self.luxury_sum_7 * Decimal(1.07)) + (self.luxury_sum_19 * Decimal(1.19))
        super().save(*args, **kwargs)

    @property
    def invoice_sum_plus_fee(self):
        if self.fee:
            return ((self.invoice_sum - (self.deposit_sum or 0) - (self.luxury_sum or 0)) * (Decimal(1.0) + self.fee / Decimal(100.0))).quantize(Decimal('0.01'))
        else:
            return self.invoice_sum


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
        return self.title


class Account(models.Model):
    title = models.CharField(max_length=255)
    inventory = models.ForeignKey('Inventory', on_delete=models.PROTECT, null=True, blank=True, related_name='account')
    additional_inventory_food = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Add. inv. food', help_text="(self.inventory.sum_inventory - self.inventory.sum_luxury) - (previous_inventory.sum_inventory - previous_inventory.sum_luxury)")
    additional_inventory_luxury = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Add. inv. luxury', help_text="self.inventory.sum_luxury - previous_inventory.sum_luxury")
    terra_luxury_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text=" terra_sums['luxury_sum'] #total luxury from terra invoices")
    luxury_consumed = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="self.terra_luxury_sum - self.additional_inventory_luxury")
    luxury_paid_diff = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Lux paid diff', help_text="user_bill_luxury_sum + self.inventory.sum_cash - self.luxury_consumed")
    user_bill_luxury_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='User bill luxury sum')
    terra_brutto_all_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Sum of all brutto terra invoice totals", verbose_name='Tot. Terra brutto (all)')
    terra_food_others_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Tot. food (others)')
    terra_food_others_fee_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Tot. food (others) + fee')
    terra_brutto_others_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Sum of all terra invoices without deposit and not from pumpwerk")
    terra_deposit_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Deposit sum')
    terra_food_pumpwerk_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    terra_food_pumpwerk_fee = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Fee food (PW)')
    food_expenses_pumpwerk_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Tot. food (PW)')
    attendance_day_sum = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Tot. days')
    previous_terra_daily_rate = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Prev. Terra rate')
    corrected_terra_daily_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='New Terra rate (+Fee)')
    
    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-inventory__inventory_date']

    def __str__(self):
        return "Account: {}".format(self.title)

    def calculate(self):
        # get relevant objects
        previous_inventory = self.inventory.get_previous_inventory()
        user_bills = UserBill.objects.filter(bill__in=self.inventory.bills.all())
        terra_invoices = TerraInvoice.objects.filter(terra_invoice_date__gt=previous_inventory.inventory_date, terra_invoice_date__lte=self.inventory.inventory_date)

        # make all the calculations
        self.attendance_day_sum = user_bills.aggregate(attendance_days_sum=Sum(F('attendance_days') * F('user__calculation_factor')))['attendance_days_sum']
        self.additional_inventory_food = (self.inventory.sum_inventory - self.inventory.sum_luxury) - (previous_inventory.sum_inventory - previous_inventory.sum_luxury)
        self.additional_inventory_luxury = self.inventory.sum_luxury - previous_inventory.sum_luxury
        
        user_bill_luxury_sum = user_bills.aggregate(luxury_sum=Sum('luxury_sum'))['luxury_sum']
        self.user_bill_luxury_sum = user_bill_luxury_sum
        terra_sums = terra_invoices.aggregate(invoice_sum=Sum('invoice_sum'), deposit_sum=Sum('deposit_sum'), luxury_sum=Sum('luxury_sum'), other_sum=Sum('other_sum'))
        self.terra_luxury_sum = terra_sums['luxury_sum'] #total luxury from terra invoices
        self.luxury_consumed = self.terra_luxury_sum - self.additional_inventory_luxury

        self.luxury_paid_diff = self.user_bill_luxury_sum + self.inventory.sum_cash - self.luxury_consumed 
        self.terra_brutto_all_sum = terra_sums['invoice_sum']
        self.terra_deposit_sum = terra_sums['deposit_sum']

        terra_brutto_others_sum = terra_invoices.filter(is_pumpwerk=False).aggregate(invoice_total=Sum(F('invoice_sum') - F('deposit_sum')))['invoice_total']
        terra_brutto_others_fee_sum = terra_invoices.filter(is_pumpwerk=False).aggregate(invoice_total=Sum((F('invoice_sum') - F('deposit_sum')) * (1.0 + F('fee') / 100.0), output_field=models.DecimalField()))['invoice_total']
        # other_invoice_deposit_sum = terra_invoices.filter(is_pumpwerk=False).aggregate(deposit_sum=Sum('deposit_sum'))['deposit_sum']
        self.terra_food_others_fee_sum = terra_brutto_others_fee_sum
        self.terra_food_others_sum = terra_brutto_others_sum
        self.terra_brutto_others_sum = terra_brutto_others_sum
        terra_food_pumpwerk_sum = terra_invoices.filter(is_pumpwerk=True).aggregate(invoice_total=Sum(F('invoice_sum') - F('deposit_sum') - F('luxury_sum')))['invoice_total']
        terra_food_pumpwerk_fee = terra_invoices.filter(is_pumpwerk=True).aggregate(invoice_total=Sum((F('invoice_sum') - F('deposit_sum') - F('luxury_sum')) * ( F('fee') / 100.0), output_field=models.DecimalField()))['invoice_total']
        self.terra_food_pumpwerk_sum = terra_food_pumpwerk_sum
        self.terra_food_pumpwerk_fee = terra_food_pumpwerk_fee
        self.food_expenses_pumpwerk_sum = self.terra_food_pumpwerk_sum - self.additional_inventory_food
        self.corrected_terra_daily_rate = (self.food_expenses_pumpwerk_sum + self.terra_food_pumpwerk_fee) / self.attendance_day_sum

        self.save()

        # delete existing UserPaybacks for acccount
        UserPayback.objects.filter(account=self).delete()
        # create all the UserPayback objects
        user_attendance_days = user_bills.values('user').order_by('user').annotate(sum_attendance_days=Sum('attendance_days'))
        for user_attendance_day in user_attendance_days:
            user = User.objects.get(pk=user_attendance_day['user'])
            user_payback, created = UserPayback.objects.get_or_create(
                user=user,
                account=self,
                total_days=user_attendance_day['sum_attendance_days'],
                total=user_attendance_day['sum_attendance_days'] * user.calculation_factor * (self.previous_terra_daily_rate - self.corrected_terra_daily_rate),
            )


class UserPayback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    total_days = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    has_paid = models.BooleanField(default=False, verbose_name='Paid?')
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'account']
        verbose_name = 'User payback'
        verbose_name_plural = 'User paybacks'
        ordering = ['-account', 'user']

    def __str__(self):
        return "User payback: {}".format(self.account.title)

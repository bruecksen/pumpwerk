
from django.db import models
from django.contrib import messages
from django.contrib import admin
from django.conf import settings
from django.forms import CheckboxSelectMultiple

from pumpwerk.food.models import Bill, UserBill, ExpenseType, Expense, Inventory, TerraInvoice, Payment, Account, UserPayback
from pumpwerk.slackbot.bot import send_message_to_channel


def calculate_bills(modeladmin, request, queryset):
    for bill in queryset:
        if UserBill.objects.filter(bill=bill, attendance_days__isnull=True).exists():
            messages.error(request, "Bill {0} is missing attendance days, skip calculation.".format(bill))
            continue
        bill.make_bill_calculation()
calculate_bills.short_description = "Calculate selected Bills"


class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_date', 'days_in_month', 'terra_daily_rate', 'member_count', 'total_attendance_days', 'total_supermarket', 'total_invest', 'total_terra', 'total_luxury', 'daily_rate')
    date_hierarchy = 'bill_date'
    readonly_fields = ('total_attendance_days', 'total_supermarket', 'total_terra', 'total_invest', 'total_luxury', 'daily_rate', 'overview')
    actions = [calculate_bills,]

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "Members"

admin.site.register(Bill, BillAdmin)

class UserBillAdmin(admin.ModelAdmin):
    list_display = ('bill_date', 'user', 'total', 'attendance_days', 'credit', 'luxury_sum', 'expense_sum', 'food_sum', 'invest_sum', 'has_paid')
    date_hierarchy = 'bill__bill_date'
    readonly_fields = ('credit',)
    list_filter = ('user',)
    list_editable = ('attendance_days', 'luxury_sum', 'has_paid')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    save_on_top = True
    list_per_page = 17

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ('food_sum', 'invest_sum', 'total', 'expense_sum')
        return readonly_fields

    def bill_date(self, obj):
        return obj.bill.bill_date
    bill_date.short_description = "Bill date"

    def expense_types_list(self, obj):
        return ', '.join([e.name for e in obj.expense_types.all()])
    expense_types_list.short_description = "Expense Types"

admin.site.register(UserBill, UserBillAdmin)


class ExpenseTypeAdmin(admin.ModelAdmin):
        list_display = ('name', 'is_invest')

admin.site.register(ExpenseType, ExpenseTypeAdmin)


class ExpenseAdmin(admin.ModelAdmin):
        list_display = ('bill_date', 'user', 'expense_type', 'amount', 'comment')

        def user(self, obj):
            return obj.user_bill.user
        user.short_description = "User"

        def bill_date(self, obj):
            return obj.user_bill.bill.bill_date
        bill_date.short_description = "Bill date"

admin.site.register(Expense, ExpenseAdmin)


class InventoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'inventory_date'
    list_display = ('inventory_date', 'sum_inventory', 'sum_cash', 'sum_luxury')

admin.site.register(Inventory, InventoryAdmin)


class PaymentAdmin(admin.ModelAdmin):
    date_hierarchy = 'payment_date'
    list_display = ('title', 'payment_date', 'payment_sum',)

admin.site.register(Payment, PaymentAdmin)


def calculate_account(modeladmin, request, queryset):
    for account in queryset:
        account.calculate()
calculate_account.short_description = "Calculate selected Accounts"

class AccountAdmin(admin.ModelAdmin):
    list_display = ('title', 'inventory_date', 'terra_food_others_sum', 'terra_food_others_fee_sum', 'terra_brutto_all_sum', 'food_expenses_pumpwerk_sum', 'terra_food_pumpwerk_fee', 'user_bill_luxury_sum', 'luxury_consumed', 'luxury_paid_diff', 'terra_deposit_sum', 'attendance_day_sum', 'previous_terra_daily_rate', 'corrected_terra_daily_rate')
    readonly_fields = ['additional_inventory_food', 'additional_inventory_luxury', 'terra_luxury_sum', 'luxury_consumed', 'luxury_paid_diff', 'terra_brutto_all_sum', 'terra_food_others_sum', 'terra_food_pumpwerk_fee', 'terra_brutto_others_sum', 'terra_deposit_sum', 'terra_food_pumpwerk_sum', 'food_expenses_pumpwerk_sum', 'attendance_day_sum', 'corrected_terra_daily_rate']
    actions = [calculate_account]

    def inventory_date(self, obj):
        return obj.inventory and obj.inventory.inventory_date
    inventory_date.short_description = "Date"

admin.site.register(Account, AccountAdmin)


class TerraInvoiceAdmin(admin.ModelAdmin):
    list_display = ('terra_invoice_date', 'invoice_number', 'invoice_sum', 'invoice_sum_plus_fee', 'deposit_sum', 'food_sum', 'luxury_sum', 'other_sum', 'is_pumpwerk', 'fee', 'is_paid')
    readonly_fields = ['luxury_sum']
    # list_filter = ('year', )

    def food_sum(self, obj):
        return obj.invoice_sum - obj.deposit_sum
    food_sum.short_description = "Food sum (inv. - dep.)"

    def is_paid(self, obj):
        return obj.payment_set.exists()
    is_paid.short_description = "Is paid?"
    is_paid.boolean = True
admin.site.register(TerraInvoice, TerraInvoiceAdmin)


class UserPaybackAdmin(admin.ModelAdmin):
    list_display = ('account', 'user', 'total_days', 'total', 'total_luxury_sum', 'has_paid')
    readonly_fields = ['user', 'account', 'total_days', 'total', 'has_paid', 'total_luxury_sum']
    list_filter = ('account',)

admin.site.register(UserPayback, UserPaybackAdmin)
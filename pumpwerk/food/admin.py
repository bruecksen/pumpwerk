
from django.db import models
from django.contrib import messages
from django.contrib import admin
from django.conf import settings
from django.forms import CheckboxSelectMultiple

from pumpwerk.food.models import Bill, UserBill, ExpenseType, Expense, Inventory, TerraInvoice, Payment, Account
from pumpwerk.slackbot.bot import send_message_to_channel


def calculate_bills(modeladmin, request, queryset):
    for bill in queryset:
        if UserBill.objects.filter(bill=bill, attendance_days__isnull=True).exists():
            messages.error(request, "Bill {0} is missing attendance days, skip calculation.".format(bill))
            continue
        bill.make_bill_calculation()
calculate_bills.short_description = "Calculate selected Bills"


def send_notification(modeladmin, request, queryset):
    for bill in queryset:
        bill.make_bill_calculation()
        if not bill.is_notified:
            send_message_to_channel(settings.SLACK_FOOD_CHANNEL, bill)
            bill.is_notified = True
            bill.save(update_fields=['is_notified'])
send_notification.short_description = "Send notification of selected Bills"



class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_date', 'days_in_month', 'terra_daily_rate', 'member_count', 'total_attendance_days', 'total_supermarket', 'total_invest', 'total_terra', 'total_luxury', 'daily_rate', 'is_notified')
    date_hierarchy = 'bill_date'
    readonly_fields = ('total_attendance_days', 'total_supermarket', 'total_terra', 'total_invest', 'total_luxury', 'daily_rate')
    actions = [calculate_bills, send_notification]

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "Members"

admin.site.register(Bill, BillAdmin)

class UserBillAdmin(admin.ModelAdmin):
    list_display = ('bill_date', 'user', 'calculation_factor', 'attendance_days', 'credit', 'expense_sum', 'food_sum', 'invest_sum', 'luxury_sum', 'total', 'has_paid')
    date_hierarchy = 'bill__bill_date'
    list_filter = ('user',)
    list_editable = ('attendance_days', 'credit', 'luxury_sum', 'has_paid')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    save_on_top = True
    list_per_page = 15

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ('food_sum', 'invest_sum', 'total', 'expense_sum')
        if obj.bill.is_notified:
            readonly_fields += ('attendance_days', 'credit', 'luxury_sum', 'calculation_factor',)
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
    list_display = ('inventory_date',  'sum_inventory', 'sum_cash', 'sum_luxury')

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
    list_display = ('title', 'inventory_date', 'terra_food_others_sum', 'terra_brutto_all_sum', 'food_expenses_pumpwerk_sum', 'luxury_paid_diff', 'terra_deposit_sum', 'attendance_day_sum', 'corrected_terra_daily_rate')
    readonly_fields = ['additional_inventory_food', 'terra_luxury_sum', 'consumed_luxury', 'luxury_paid_diff', 'terra_brutto_all_sum', 'terra_food_others_sum', 'terra_brutto_others_sum', 'terra_deposit_sum', 'terra_food_pumpwerk_sum', 'food_expenses_pumpwerk_sum', 'attendance_day_sum', 'corrected_terra_daily_rate']
    actions = [calculate_account]

    def inventory_date(self, obj):
        return obj.inventory.inventory_date
    inventory_date.short_description = "Date"

admin.site.register(Account, AccountAdmin)


class TerraInvoiceAdmin(admin.ModelAdmin):
    list_display = ('terra_invoice_date', 'invoice_number', 'invoice_sum', 'deposit_sum', 'luxury_sum', 'other_sum', 'is_pumpwerk', 'is_paid')
    # list_filter = ('year', )

    def is_paid(self, obj):
        return obj.payment_set.exists()
    is_paid.short_description = "Is paid?"
    is_paid.boolean = True
admin.site.register(TerraInvoice, TerraInvoiceAdmin)
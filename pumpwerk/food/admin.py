
from django.db import models
from django.contrib import messages
from django.contrib import admin
from django.conf import settings
from django.forms import CheckboxSelectMultiple

from pumpwerk.food.models import Bill, UserBill, ExpenseType, Expense
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
    list_display = ('month', 'year', 'days_in_month', 'terra_daily_rate', 'member_count', 'total_attendance_days', 'total_supermarket', 'total_invest', 'total_terra', 'total_luxury', 'daily_rate', 'is_notified')
    list_filter = ('year', )
    readonly_fields=('total_attendance_days', 'total_supermarket', 'total_terra', 'total_invest', 'total_luxury', 'daily_rate')
    actions = [calculate_bills, send_notification]

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "Members"

admin.site.register(Bill, BillAdmin)

class UserBillAdmin(admin.ModelAdmin):
    list_display = ('bill_year', 'bill_month', 'user', 'calculation_factor', 'expense_types_list', 'attendance_days', 'credit', 'food_sum', 'invest_sum', 'luxury_sum', 'total', 'has_payed')
    list_filter = ('bill__year', 'bill__month', 'user')
    list_editable = ('attendance_days', 'credit', 'luxury_sum', 'has_payed')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ('food_sum', 'invest_sum', 'total')
        if obj.bill.is_notified:
            readonly_fields += ('attendance_days', 'credit', 'luxury_sum', 'calculation_factor',)
        return readonly_fields

    def bill_year(self, obj):
        return obj.bill.year
    bill_year.short_description = "Year"

    def bill_month(self, obj):
        return obj.bill.get_month()
    bill_month.short_description = "Month"

    def expense_types_list(self, obj):
        return ', '.join([e.name for e in obj.expense_types.all()])
    expense_types_list.short_description = "Expense Types"

admin.site.register(UserBill, UserBillAdmin)


class ExpenseTypeAdmin(admin.ModelAdmin):
        list_display = ('name', 'is_invest')

admin.site.register(ExpenseType, ExpenseTypeAdmin)


class ExpenseAdmin(admin.ModelAdmin):
        list_display = ('year', 'month', 'user', 'expense_type', 'amount')

        def user(self, obj):
            return obj.user_bill.user
        user.short_description = "User"

        def year(self, obj):
            return obj.user_bill.bill.year
        user.year = "Year"

        def month(self, obj):
            return obj.user_bill.bill.get_month()
        user.month = "Month"

admin.site.register(Expense, ExpenseAdmin)
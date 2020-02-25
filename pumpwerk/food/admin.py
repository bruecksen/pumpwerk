from django.contrib import admin
from django.utils.dates import MONTHS

from pumpwerk.food.models import Bill, UserBill, ExpenseType, Expense


class BillAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'days_in_month', 'terra_daily_rate', 'member_count')
    list_filter = ('year', )

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "Members"

admin.site.register(Bill, BillAdmin)

class UserBillAdmin(admin.ModelAdmin):
    list_display = ('bill_year', 'bill_month', 'user', 'attendance_days', 'total', 'has_payed', 'is_notified')
    list_filter = ('bill__year', 'bill__month')

    def bill_year(self, obj):
        return obj.bill.year
    bill_year.short_description = "Year"

    def bill_month(self, obj):
        return MONTHS[obj.bill.month]
    bill_month.short_description = "Month"

admin.site.register(UserBill, UserBillAdmin)


class ExpenseTypeAdmin(admin.ModelAdmin):
        list_display = ('name', 'is_invest')

admin.site.register(ExpenseType, ExpenseTypeAdmin)


class ExpenseAdmin(admin.ModelAdmin):
        list_display = ('expense_type', 'user_bill', 'amount')

admin.site.register(Expense, ExpenseAdmin)
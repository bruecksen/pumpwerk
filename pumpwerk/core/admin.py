from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from solo.admin import SingletonModelAdmin

from pumpwerk.core.models import User, Setting

class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('calculation_factor',)
    fieldsets = UserAdmin.fieldsets + (('Calculation', {'fields': ('calculation_factor',)}),)


admin.site.register(User, CustomUserAdmin)

admin.site.register(Setting, SingletonModelAdmin)
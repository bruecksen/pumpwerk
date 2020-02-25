from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from solo.admin import SingletonModelAdmin

from pumpwerk.core.models import User, Setting

admin.site.register(User, UserAdmin)

admin.site.register(Setting, SingletonModelAdmin)
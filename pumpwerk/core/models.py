from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from django.db import models
from django.conf import settings

from solo.models import SingletonModel


class User(AbstractUser):
    calculation_factor = models.DecimalField(max_digits=8, decimal_places=2, default=1)


class Setting(SingletonModel):
    terra_daily_rate = models.DecimalField(max_digits=8, decimal_places=2, default=6.0)
    active_members = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return "Settings"

    class Meta:
        verbose_name = "Settings"
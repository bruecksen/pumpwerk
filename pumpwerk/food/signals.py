from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from pumpwerk.food.models import Bill, UserBill, ExpenseType

User = get_user_model()


@receiver(m2m_changed, sender=Bill.members.through)
def create_user_bill_objects(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            user = User.objects.get(pk=pk)
            user_bill, created = UserBill.objects.get_or_create(
                bill=instance,
                user=user,
                calculation_factor=user.calculation_factor,
            )
            if created:
                user_bill.expense_types.add(*list(ExpenseType.objects.all()))
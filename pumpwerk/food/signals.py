from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from pumpwerk.food.models import Bill, UserBill, ExpenseType, UserPayback

User = get_user_model()


@receiver(m2m_changed, sender=Bill.members.through)
def create_user_bill_objects(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            user = User.objects.get(pk=pk)
            user_credit = 0
            if instance.account_carry_over and UserPayback.objects.filter(user=user, account=instance.account_carry_over).exists():
                # carry over positive and negative userpayback total
                user_credit += UserPayback.objects.get(user=user, account=instance.account_carry_over).total
            if instance.bill_carry_over and UserBill.objects.filter(user=user, bill=instance.bill_carry_over).exists():
                last_user_bill = UserBill.objects.get(user=user, bill=instance.bill_carry_over)
                if last_user_bill.get_user_credit():
                    user_credit += last_user_bill.get_user_credit()
            user_bill, created = UserBill.objects.get_or_create(
                bill=instance,
                user=user,
                calculation_factor=user.calculation_factor,
                credit=user_credit,
            )
            if created:
                user_bill.expense_types.add(*list(ExpenseType.objects.all()))
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from debts.models import Debt, StatusLog
from users.models import Notification, NotificationStatus
# Enter your code here

@receiver(post_save, sender=Debt)
def send_notification(sender, instance, created, *args, **kwargs):
    # debt status changed
    if not created and hasattr(instance, "_pervious_status") and hasattr(instance, "_user"):

        def create_status_log_and_notifications():
            user = getattr(instance, "_user")
            pervious_status = getattr(instance, "_pervious_status")

            StatusLog.objects.create(
                user=user,
                debt=instance,
                from_status=pervious_status,
                to_status=instance.status
                )
            
            static_data = {"status": NotificationStatus.UNREAD,
                           "title": "Debt Status Changed.",
                           "text": f"debt status changed from {pervious_status} to {instance.status} bu {user}."}
            notification = [Notification(reciver=instance.debtor, **static_data), Notification(reciver=instance.creditor, **static_data)]
            Notification.objects.bulk_create(notification)

        transaction.on_commit(create_status_log_and_notifications)

        if hasattr(instance, "_pervious_status"): del instance._pervious_status
        if hasattr(instance, "_user"): del instance._user

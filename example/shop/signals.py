from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver

from salesman.orders.signals import status_changed


@receiver(status_changed)
def send_notification(sender, order, new_status, old_status, **kwargs):
    """
    Send notification to customer when order is completed.
    """
    if new_status == order.statuses.COMPLETED:
        subject = f"Order '{order}' is completed"
        message = "Thank you for shopping with Salesman!"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email])

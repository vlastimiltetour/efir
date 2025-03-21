import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.mail_confirmation import (order_shipped,
                                      send_paid_offer_confirmation, customer_order_email_confirmation)
from orders.models import Order

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_email_when_order_completed(sender, instance, created, **kwargs):
    logger.info(f"======= Order {instance.id} has been updated.")

    # Check if the order is marked as shipped and the shipped email hasn't been sent
    if instance.shipped and not instance.shipped_sent:
        order_shipped(instance.id)
        logger.info(
            f"======= Order {instance.id} has been dispatched to transport service."
        )

        # Update the 'shipped_sent' field without triggering the signal again
        Order.objects.filter(pk=instance.pk).update(shipped_sent=True)


@receiver(post_save, sender=Order)
def send_email_when_order_paid(sender, instance, **kwargs):
    logger.info(f"======= Order {instance.id} has been updated - paid.")

    # Check if the order is marked as shipped and the shipped email hasn't been sent
    if instance.paid and not instance.paid_confirmation_sent:
        customer_order_email_confirmation(order_id=instance.id)
        logger.info(
            f"======= Order {instance.id} has been dispatched to transport service."
        )
        Order.objects.filter(id=instance.id).update(paid_confirmation_sent=True)

        # Update the field confirmation_sent

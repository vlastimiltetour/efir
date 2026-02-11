import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.mail_confirmation import (customer_order_email_confirmation,
                                      order_shipped,
                                      unpaid_customer_order_email_confirmation)
from orders.models import Order

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_email_when_order_created(sender, instance, **kwargs):
    # Check if the order is marked as shipped and the shipped email hasn't been sent
    if instance.created and not instance.confirmation_sent:
        logger.info(f"======= Order {instance.id} has been created.")
        try:
            unpaid_customer_order_email_confirmation(instance.id)
            logger.info(
                f"======= Order {instance.id} has been created and email confirmation has been sent."
            )

            # Update the 'shipped_sent' field without triggering the signal again
            Order.objects.filter(pk=instance.pk).update(confirmation_sent=True)
        except Exception as e:
            logger.error(f"There has been an error while triggering signal and sending an confirmatory email in order {instance.id}, error: {e}")
    
@receiver(post_save, sender=Order)
def send_email_when_order_completed(sender, instance, created, **kwargs):
    # Check if the order is marked as shipped and the shipped email hasn't been sent
    if instance.shipped and not instance.shipped_sent:
        logger.info(f"======= Order {instance.id} has been updated.")
        order_shipped(instance.id)
        logger.info(
            f"======= Order {instance.id} has been dispatched to transport service."
        )

        # Update the 'shipped_sent' field without triggering the signal again
        Order.objects.filter(pk=instance.pk).update(shipped_sent=True)


@receiver(post_save, sender=Order)
def send_email_when_order_paid(sender, instance, **kwargs):
    # Check if the order is marked as shipped and the shipped email hasn't been sent
    if instance.paid and not instance.paid_confirmation_sent:  # TODO vlk test this
        logger.info(f"======= Order {instance.id} has been updated - paid.")
        customer_order_email_confirmation(order_id=instance.id)
        logger.info(
            f"======= Order {instance.id} has been dispatched to transport service."
        )
        Order.objects.filter(id=instance.id).update(paid_confirmation_sent=True)

        # Update the field confirmation_sent

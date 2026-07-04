import logging

from django.utils import timezone

from orders.models import Order

from .mail_confirmation import order_cancellation

logger = logging.getLogger(__name__)


class OrderStatusService:
    @classmethod
    def update_status(cls, order, status):
        Order.objects.filter(pk=order.pk).update(status=status)

    @staticmethod
    def mark_as_received(order):
        if not order.paid:
            return

        order.status = "P"  # Potvrzeno
        order.save(update_fields=["status"])

    @staticmethod
    def mark_as_paid(order):
        if order.paid:
            return

        order.status = "Z"  # Zaplaceno
        order.save(update_fields=["status"])

    @staticmethod
    def mark_as_shipped(order):
        if order.shipped:
            return

        order.status = "V"  # Potvrzeno
        order.save(update_fields=["status"])

    # https://medium.com/@sizanmahmud08/django-signals-the-complete-guide-to-building-responsive-event-driven-applications-775cc7cb1618
    @staticmethod
    def mark_as_cancelled(order):
        if order.cancelled:
            logger.info(
                f" === Order {order.id} has been already CANCELLED. NO NEED TO CANCEL AGAIN."
            )
            return

        order.cancelled = timezone.now()

        order.status = "S"
        order.save(update_fields=["status", "cancelled"])
        order_cancellation(order_id=order.id)
        logger.info(f" === Order {order.id} has been cancelled.")

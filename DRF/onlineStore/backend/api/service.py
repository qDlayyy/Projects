import logging
from datetime import timedelta, datetime


logger = logging.getLogger(__name__)


def get_delivery_date():
    FIXED_DELIVERY_DAYS_GAP = 3
    FIXED_DELIVERY_HOURS = 20

    today = datetime.now()
    delivery_date = today + timedelta(days=FIXED_DELIVERY_DAYS_GAP)

    if delivery_date.weekday() == 5:
        delivery_date += timedelta(days=2)
    
    elif delivery_date.weekday() == 6:
        delivery_date += timedelta(days=1)
    

    delivery_date = delivery_date.replace(hour=FIXED_DELIVERY_HOURS, minute=0, second=0, microsecond=0)

    return delivery_date


def adjust_delivery_notification(order):
    delivery_date = get_delivery_date()
    gap = order.notification_time
    notification_time = int(gap[:-1])
    delivery_notification = delivery_date - timedelta(hours=notification_time)

    logger.info(f'\nDelivery Notification Date: {delivery_notification}. Chosen Delivery Notification Gap: {order.notification_time}\n')

    return delivery_notification
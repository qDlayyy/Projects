from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Order
from datetime import timedelta, timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_registration_confimation_email(comfirmation_link, user_email):
    subject = 'Registration Confirmation'
    message = f'Follow the link to finish the profile creation: {comfirmation_link}'
    from_email = 'test@gmail.com'
    recipient_list = [user_email]

    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)


@shared_task
def send_order_confirmation_email(user_email, order_id):
    subject = f'Order Confirmation'
    message = f'Your order has been successfully created! Order: #{order_id}'
    email_from = 'test@gmail.com'
    recipient_list = [user_email]

    send_mail(subject=subject, message=message, from_email=email_from, recipient_list=recipient_list)


@shared_task
def send_weekly_email():
    subscribers = Profile.objects.filter(is_subscribed=True)

    for subscriber in subscribers:

        subject = 'Sales Letter!'
        message = f'Hello, {subscriber.user.username}! We are happy you\'ve agreed on our super interesting newsletter.'
        from_email = 'test@gmail.com'
        recipient_list = [subscriber.user.email]

        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)


@shared_task
def send_pre_delivery_email(order_id, user_email):
    try:
        order = Order.objects.get(pd=order_id)
        FIXED_DELIVERY_TIME = 20
        notify_time = int(order.notification_time[:-1])

        notification_time = FIXED_DELIVERY_TIME - timedelta(hours=notify_time)

        if timezone.now() >= notification_time:
            subject = 'Delivery is comming!'
            message = f'Your order is delivered in {notify_time} hours!'
            from_email = 'test@gmail.com'
            recipient_list = [user_email]

            send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
    
    except Exception as e:
        logger.error(f'Error: {e}')

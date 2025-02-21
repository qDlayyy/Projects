from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_verification_email(user_email, link):
    subject = 'Verification Email'
    message = f'Follow the link to create the account: {link}'
    from_email = 'test@gmail.com'
    list_of_emails = [user_email]

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=list_of_emails
    )
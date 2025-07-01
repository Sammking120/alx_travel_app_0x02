from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_payment_confirmation_email(email, booking_reference):
    subject = "Payment Confirmation"
    message = f"Your payment with reference {booking_reference} was successful. Thank you!"
    send_mail(subject, message, 'no-reply@yourdomain.com', [email])

from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_payment_confirmation_email(email, booking_reference):
    subject = "Payment Confirmation"
    message = f"Your payment with reference {booking_reference} was successful. Thank you!"
    send_mail(subject, message, 'no-reply@yourdomain.com', [email])


@shared_task
def send_booking_confirmation_email(to_email, booking_details):
    subject = 'Booking Confirmation'
    message = f"Your booking was successful!\n\nDetails:\n{booking_details}"
    from_email = 'no-reply@alxtravel.com'

    send_mail(subject, message, from_email, [to_email])
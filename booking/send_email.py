from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_booking_notification(user_email, booking_id):
    # activation_url = f'http://127.0.0.1:8000/booking/confirm/{booking_id}/'
    activation_url = f'http://localhost:3000/booking/confirm/{booking_id}/'
    context = {'activation_url': activation_url}
    subject = 'Please confirm the booking!'
    html_message = render_to_string('booking.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'kayakta@gmail.com',
        [user_email],
        html_message=html_message,
        fail_silently=True
    )

from django.core.mail import send_mail
from django.utils.html import format_html
from django.conf import settings
from twilio.rest import Client
from django.template.loader import render_to_string
from django.utils.html import strip_tags

account_sid = settings.TWILIO_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_sender = settings.TWILIO_SENDER_PHONE


def send_confirmation_email(email, code):
    activation_url = f'http://localhost:3000/api/account/activate/?u={code}'
    context = {'activation_url': activation_url}
    subject = 'Hello, please confirm your email.'
    html_message = render_to_string('email_activate.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'admin@gmail.com',
        [email],
        html_message=html_message,
        fail_silently=True
    )

def send_confirmation_password(email, code):
    activation_url = f'http://localhost:3000/api/account/reset-password/confirm/{code}/'
    context = {'activation_url': activation_url}
    subject = 'Hello, please confirm the new password.'
    html_message = render_to_string('new_password.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'admin@gmail.com',
        [email],
        html_message=html_message,
        fail_silently=True
    )

def send_activation_sms(phone_number, activation_code):
    message = f'Your activation code: {activation_code}'
    client = Client(account_sid, auth_token)
    client.messages.create(body=message, from_=twilio_sender, to=phone_number)
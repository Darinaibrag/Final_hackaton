from django.core.mail import send_mail
from django.utils.html import format_html
from django.conf import settings
from twilio.rest import Client

account_sid = settings.TWILIO_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_sender = settings.TWILIO_SENDER_PHONE


def send_confirmation_email(email, code):
    activation_url = f'http://13.49.223.191/api/account/activate/?u={code}'
    message = format_html(
        'Здравствуйте, активируйте ваш аккаунт! '
        'Чтобы активировать ваш аккаунт, перейдите по ссылке:'
        '<br>'
        '<a href="{}"></a>'
        '<br>'
        'Не передавайте этот код никому!',
        activation_url,
    )

    send_mail(
        'Здравствуйте, активируйте ваш аккаунт!',
        message,
        'johnsnowtest73@gmail.com',
        [email],
        fail_silently=False,
    )

def send_activation_sms(phone_number, activation_code):
    message = f'Ваш код активации: {activation_code}'
    client = Client(account_sid, auth_token)
    client.messages.create(body=message, from_=twilio_sender, to=phone_number)
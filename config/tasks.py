from account.send_email import send_confirmation_email, send_activation_sms

from .celery import app

@app.task()
def send_connfirmation_email_task(email, code):
    send_confirmation_email(email, code)

@app.task()
def send_activation_sms_task(phone_number, activation_code):
    send_activation_sms(phone_number, activation_code)

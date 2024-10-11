from django.core.mail import send_mail
from django.conf import settings

def send_password_in_email(to_email, password):
    subject = 'Você foi cadastrado no sistema de presença do cursinho'
    message = f'Sua conta foi criada com sucesso. Sua senha é: {password}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [to_email]
    send_mail(subject, message, email_from, recipient_list)
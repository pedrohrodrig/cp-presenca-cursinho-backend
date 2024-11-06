import os
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from .managers import UserManager

class Roles(models.IntegerChoices):
    ADMIN = 0, "Administrador"
    TEACHER = 1, "Professor"
    STUDENT = 2, "Aluno"
    OTHERS = 3, "Outros"

    @classmethod
    def convert_to_int_if_string(cls, role):
        if isinstance(role, int):
            return role
        
        role_map = {label: value for value, label in cls.choices}
        return role_map.get(role, cls.OTHERS)


class User(AbstractBaseUser, PermissionsMixin):   
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    role = models.IntegerField(choices=Roles.choices, blank=False, null=False, default=Roles.OTHERS)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name
    
    def get_short_name(self):
        return self.first_name

@receiver(reset_password_token_created)
def password_reset_token_created(reset_password_token, register=False, *args, **kwargs):
    sitelink = os.getenv("FRONTEND_SITE_LINK", "http://localhost:5173/")
    token = "{}".format(reset_password_token.key)
    full_link = str(sitelink) + str("login/password-reset/") + str(token)

    context = {
        'full_link': full_link,
    }

    subject = "Solicitação de redefinição de senha" if not register else "Boas vindas ao Sistema de Presença do CP!"
    html_template = 'reset-password-email.html' if not register else 'set-password-email.html'

    html_message = render_to_string(html_template, context=context)
    plain_message = strip_tags(html_message)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=os.getenv("EMAIL_HOST_USER"),
        to=[reset_password_token.user.email],
    )

    msg.attach_alternative(html_message, "text/html")
    msg.send()
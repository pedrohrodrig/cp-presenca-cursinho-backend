from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

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

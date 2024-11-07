from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

from .models import User
from attendance.models import StudentClass

def duplicated_email_validation(email):
    users = User.objects.filter(email=email)

    if users.exists():
        raise ValidationError({"email": _("This email address is already registered for another user")})

def password_confirmation_validation(password, password_confirmation):
    if password and password_confirmation and password != password_confirmation:
        raise ValidationError({"password": _("Password and Confirmation must be identical")})
    
    try:
        password_validation.validate_password(password)
    except Exception as e:
        raise ValidationError({"password": e})
    
def student_class_exists_validation(student_class):
    if isinstance(student_class, int):
        student_class = StudentClass.objects.filter(id=student_class).first()
    else:
        try:
            student_class_id = int(student_class)
            student_class = StudentClass.objects.filter(id=student_class_id).first()
        except ValueError:
            student_class = StudentClass.objects.filter(name=student_class).first()

    if not student_class:
        raise ValidationError({"student_class": _("This class does not exist")})
    
    return student_class
import random

from django.core.mail import send_mail
from django.template.loader import get_template
import string


def send_mail_to_user(subject, template_path, context, from_email, to_email):

    template = get_template(template_path)

    body = template.render(context)

    send_mail(subject, body, from_email, [to_email], fail_silently=False)


def generate_validation_code(user):

    all_numbers = string.digits + string.ascii_letters

    code = ''

    for i in range(6):
        code = code + random.choice(all_numbers)

    user.validate_code = code
    user.save()


def generate_change_password_code(user):

    all_numbers = string.digits + string.ascii_letters

    code = ''

    for i in range(6):
        code = code + random.choice(all_numbers)

    user.password_change_code = code
    user.save()

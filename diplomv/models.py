from django.utils import timezone

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from .validators import validate_file_extension


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        print(2)
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        print(1)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField('Дата создания', default=timezone.now)
    first_name = models.CharField('Имя', max_length=30, blank=True)
    last_name = models.CharField('Фамилия', max_length=30, blank=True)
    identifier = models.CharField('Идентификатор', max_length=255)
    avatar = models.ImageField(upload_to='user_avatars/', null=True, blank=True, verbose_name='Фото')
    uuid = models.CharField('UUID', max_length=255)
    events = models.ManyToManyField('Event', related_name='events', verbose_name='События пользователя', null=True)
    changeUserInfoDelay = models.DateField('Дата последнего изменения профиля', null=True)
    changeDeviceDelay = models.DateField('Дата смены залогиненого устройства', null=True)

    validate_code = models.CharField('Код валидации при регистрации', max_length=6, null=True)
    password_change_code = models.CharField('Код для смены пароля', max_length=6, null=True)

    can_change_password = models.BooleanField('Возможность сменить пароль', null=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)


"""def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)"""


# Create your models here.

class Event(models.Model):
    name = models.CharField('Название события', max_length=50)
    event_description = models.CharField('Описание', max_length=255)

    date = models.DateTimeField('Дата и время окончания события')
    startTime = models.CharField('Время начала', max_length=255)
    finishTime = models.CharField('Время окончания', max_length=255)
    creator = models.ForeignKey('User', verbose_name='Создатель', related_name='creator',
                                  null=True, blank=True, on_delete=models.SET_NULL)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Долгота')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Широта')
    registrationRadius = models.IntegerField('Радиус регистрации')

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "Событие"

    def __str__(self):
        return self.name

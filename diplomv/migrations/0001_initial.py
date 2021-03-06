# Generated by Django 2.2.2 on 2020-06-16 10:26

import diplomv.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='Email address')),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='Фамилия')),
                ('identifier', models.CharField(max_length=255, verbose_name='Идентификатор')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='user_avatars/', verbose_name='Фото')),
                ('uuid', models.CharField(max_length=255, verbose_name='UUID')),
                ('changeUserInfoDelay', models.DateField(null=True, verbose_name='Дата последнего изменения профиля')),
                ('changeDeviceDelay', models.DateField(null=True, verbose_name='Дата смены залогиненого устройства')),
                ('validate_code', models.CharField(max_length=6, null=True, verbose_name='Код валидации при регистрации')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', diplomv.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название события')),
                ('description', models.CharField(max_length=255, verbose_name='Описание')),
                ('date', models.DateTimeField(verbose_name='Дата и время окончания события')),
                ('startTime', models.CharField(max_length=255, verbose_name='Время начала')),
                ('finishTime', models.CharField(max_length=255, verbose_name='Время окончания')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Долгота')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Широта')),
                ('registrationRadius', models.IntegerField(verbose_name='Радиус регистрации')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
            ],
            options={
                'verbose_name': 'Событие',
                'verbose_name_plural': 'Событие',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='events',
            field=models.ManyToManyField(related_name='events', to='diplomv.Event', verbose_name='События пользователя'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]

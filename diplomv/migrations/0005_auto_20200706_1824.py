# Generated by Django 2.2.2 on 2020-07-06 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diplomv', '0004_auto_20200706_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, default='/media/diplomv/user_avatars/default_avatar.png', null=True, upload_to='user_avatars/', verbose_name='Фото'),
        ),
    ]

# Generated by Django 2.2.2 on 2020-07-06 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diplomv', '0007_auto_20200706_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='my_events',
            field=models.ManyToManyField(null=True, related_name='my_events', to='diplomv.Event', verbose_name='События пользователя'),
        ),
    ]
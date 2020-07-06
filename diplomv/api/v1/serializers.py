import datetime

from django.contrib.auth import authenticate
from rest_framework import serializers, status, exceptions
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.utils.translation import gettext_lazy as _

from diplomv import utils, settings
from diplomv.models import User, Event

class CustomAuthTokenSerializer(AuthTokenSerializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    uuid = serializers.CharField(label=_("UUID"), required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'identifier', 'avatar', 'uuid')
        search_fields = ['pk', 'events']

    def create(self, validated_data):
        print(validated_data)
        try:
            is_uuid_exists = User.objects.get(uuid=validated_data['uuid'])
            raise exceptions.NotAuthenticated('Cant register multiply users in one device')
        except Exception as e:
            print(e)
            user = User.objects.create_user(**validated_data)
            user.changeDeviceDelay = datetime.date.today()
            user.changeUserInfoDelay = datetime.date.today()
            user.save()
        return user

    """def save(self, **kwargs):
        assert not hasattr(self, 'save_object'), (
                'Serializer `%s.%s` has old-style version 2 `.save_object()` '
                'that is no longer compatible with REST framework 3. '
                'Use the new-style `.create()` and `.update()` methods instead.' %
                (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        # Guard against incorrect use of `serializer.save(commit=False)`
        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        assert not hasattr(self, '_data'), (
            "You cannot call `.save()` after accessing `serializer.data`."
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(validated_data)
            assert self.instance is not None, (
                '`create()` did not return an object instance.'
            )

        print("------------------------------------------")
        subject = 'Подверждение регистрации'
        template = 'diplomv/visitor_code_email.txt'
        context = {
            'user': self.instance
        }
        utils.generate_validation_code(self.instance)

        utils.send_mail_to_user(subject, template, context, settings.SERVICE_EMAIL, self.instance.email)

        return self.instance"""


class GetUserByTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255, required=True)


class UserChangeInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    identifier = serializers.CharField(max_length=255, required=True)


class RegisterToEventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)

    user_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    user_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)


class GetUserEvents(serializers.Serializer):
    token = serializers.CharField(max_length=255, required=True)
    is_finished = serializers.BooleanField(required=True)


class UserChangePasswordSendValidationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserChangePasswordValidateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    code = serializers.CharField(required=True, max_length=6)


class UserChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('pk', 'name', 'event_description', 'date', 'startTime', 'finishTime', 'latitude',
                  'longitude', 'registrationRadius')

    def save(self, **kwargs):
        assert not hasattr(self, 'save_object'), (
                'Serializer `%s.%s` has old-style version 2 `.save_object()` '
                'that is no longer compatible with REST framework 3. '
                'Use the new-style `.create()` and `.update()` methods instead.' %
                (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        # Guard against incorrect use of `serializer.save(commit=False)`
        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        assert not hasattr(self, '_data'), (
            "You cannot call `.save()` after accessing `serializer.data`."
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(validated_data)
            assert self.instance is not None, (
                '`create()` did not return an object instance.'
            )
        user = self.context['request'].user
        self.instance.creator = user
        self.instance.save()
        return self.instance


class GetUsersInEventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)


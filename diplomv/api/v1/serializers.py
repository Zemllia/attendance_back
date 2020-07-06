from rest_framework import serializers

from diplomv import utils, settings
from diplomv.models import User, Event


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'identifier', 'avatar', 'uuid')
        search_fields = ['pk', 'events']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
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


class UserChangeInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    identifier = serializers.CharField(max_length=255, required=True)


class RegisterToEventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)

    user_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    user_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)


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


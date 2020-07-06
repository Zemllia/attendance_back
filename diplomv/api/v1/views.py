import decimal
import geopy.distance

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import viewsets, mixins, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings as drf_settings

from diplomv import utils, settings
from diplomv.api.v1.serializers import UserSerializer, EventSerializer, UserValidationSerializer, \
    UserChangeInfoSerializer, UserChangePasswordSendValidationSerializer, UserChangePasswordSerializer, \
    UserChangePasswordValidateSerializer, RegisterToEventSerializer
from diplomv.models import *


class DiplomvViewSetMixin(object):
    serializer_classes = {}
    action = None
    querysets = {}
    queryset = None
    serializer_class = None
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_classes.get('default', self.serializer_class))
    def get_queryset(self):
        return self.querysets.get(self.action, self.querysets.get('default', self.queryset))


class UserViewSet(DiplomvViewSetMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """search_fields = ['email']
    """

    search_fields = ['name', 'pk', 'events']
    filter_backends = (filters.SearchFilter,)

    serializer_class = UserSerializer
    serializer_classes = {
        'update_user_info': UserChangeInfoSerializer,
        'user_change_password_send_validation': UserChangePasswordSendValidationSerializer,
        'user_change_password_validate': UserChangePasswordValidateSerializer,
        'user_change_password': UserChangePasswordSerializer,
        'register_to_event': RegisterToEventSerializer
    }
    queryset = User.objects.all()
    permission_classes = ()

    @action(detail=False, methods=['put'], name='Update user info')
    def update_user_info(self, request):
        try:
            request.user.first_name = request.data['first_name']
            request.user.last_name = request.data['last_name']
            request.user.identifier = request.data['identifier']
        except Exception as e:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], name='Update user info')
    def register_to_event(self, request):
        event_id = request.data['event_id']

        try:
            event = Event.objects.get(pk=event_id)
        except Exception as e:
            return Response({'status': 'error', 'message': 'no event with given id'},
                            status=status.HTTP_400_BAD_REQUEST)
        lon1 = (decimal.Decimal(request.data['user_longitude']))
        lat1 = (decimal.Decimal(request.data['user_latitude']))
        lon2 = (decimal.Decimal(event.longitude))
        lat2 = (decimal.Decimal(event.latitude))
        coordinates1 = (lat1, lon1)
        coordinates2 = (lat2, lon2)
        distance = geopy.distance.vincenty(coordinates1, coordinates2).meters
        if distance > event.registrationRadius:
            return Response({'status': 'error', 'message': 'no event with given id'}, status=status.HTTP_409_CONFLICT)

        if event in request.user.events.all():
            return Response({'status': 'error', 'message': 'you already registered to this event'},
                            status=status.HTTP_409_CONFLICT)

        request.user.events.add(event)
        request.user.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], name='Update user password')
    def user_change_password_send_validation(self, request):
        user_email = request.data['email']
        try:
            user = User.objects.get(email=user_email)
        except Exception as e:
            return Response({'status': 'error', 'message': 'user not found'}, status=status.HTTP_400_BAD_REQUEST)

        subject = 'Подверждение смены пароля'
        template = 'diplomv/change_password_email.txt'
        context = {
            'user': user
        }
        utils.generate_change_password_code(user)

        utils.send_mail_to_user(subject, template, context, settings.SERVICE_EMAIL, user.email)

        return Response({'status': 'success', 'user_id': user.pk}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], name='Update user info')
    def user_change_password_validate(self, request):
        user_id = request.data['user_id']
        code = request.data['code']
        try:
            user = User.objects.get(pk=user_id)
            if str(user.password_change_code) == str(code):
                user.can_change_password = True
                user.password_change_code = None
                user.save()
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'wrong validation code'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': 'user not found'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], name='Update user info')
    def user_change_password(self, request):
        user_id = request.data['user_id']
        new_password = request.data['new_password']
        try:
            user = User.objects.get(pk=user_id)
        except Exception as e:
            return Response({'status': 'error', 'message': 'user not found'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.can_change_password:
            return Response({'status': 'error', 'message': 'not validated'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response({'status': 'error', 'message': e}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.can_change_password = False
        user.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class EventViewSet(mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """search_fields = ['email']
    filter_backends = (filters.SearchFilter,)"""

    search_fields = ['pk']

    serializer_class = EventSerializer
    queryset = Event.objects.all()



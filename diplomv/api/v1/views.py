import decimal
import datetime

import geopy.distance

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import viewsets, mixins, status, filters, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_auth.views import LoginView
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings as drf_settings
from rest_framework.views import APIView
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView

from diplomv import utils, settings
from diplomv.api.v1.serializers import UserSerializer, EventSerializer, \
    UserChangeInfoSerializer, UserChangePasswordSendValidationSerializer, UserChangePasswordSerializer, \
    UserChangePasswordValidateSerializer, RegisterToEventSerializer, CustomAuthTokenSerializer, \
    GetUserByTokenSerializer, GetUserEvents
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


class UserCodeLoginView(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="username",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid username for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
                coreapi.Field(
                    name="UUID",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="UUID",
                        description="Valid UUID of device",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if request.data['UUID'] != user.uuid:
            print(datetime.date.today() - datetime.timedelta(days=7))
            if user.changeDeviceDelay > datetime.date.today() - datetime.timedelta(days=7):
                return Response({'status': 'error', 'message': 'Cant change device'})
            else:
                user.uuid = request.data['UUID']
                user.changeDeviceDelay = datetime.date.today()
                user.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


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
        'register_to_event': RegisterToEventSerializer,
        'get_user_by_token': GetUserByTokenSerializer,
        'get_user_events': GetUserEvents
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

    @action(detail=False, methods=['post'], name='Update user info')
    def get_user_by_token(self, request):
        try:
            token = request.data['token']
        except Exception as e:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(auth_token=token)
        except Exception as e:
            print(e)
            return Response({'status': 'error', 'message': 'no such user'})
        user_avatar = None
        if user.avatar != '':
            user_avatar = user.avatar
        return Response({'pk': user.pk, 'email': user.email, 'firs_name': user.first_name, 'last_name': user.last_name,
                         'identifier': user.identifier, 'avatar': user_avatar, 'uuid': user.uuid}, status=status.HTTP_200_OK)


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

    def get_user_events(self, request):
        token = request.data['event_id']
        is_finished = request.data['is_finished']

        events = User.objects.get(auth_token=token).events
        print(events)

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



from django.conf.urls import url
from django.urls import path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from diplomv.api.v1 import views as main_views
from rest_framework.authtoken import views

from diplomv.api.v1.views import UserCodeLoginView
from diplomv.schema import CoreAPISchemaGenerator

router = routers.SimpleRouter()
router.register(r'user', main_views.UserViewSet)
router.register(r'event', main_views.EventViewSet)

api_urlpatterns = router.urls + [
    url(r'^auth/', UserCodeLoginView.as_view()),
    path('doc/', include_docs_urls(title='API', authentication_classes=[], permission_classes=[],
                                         generator_class=CoreAPISchemaGenerator))
]

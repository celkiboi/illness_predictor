from django.contrib import admin
from django.urls import path, re_path
from .views import illness_predictor_view
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', illness_predictor_view, name="illness_predictor"),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]

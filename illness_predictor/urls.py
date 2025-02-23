from django.contrib import admin
from django.urls import path
from .views import illness_predictor_view

urlpatterns = [
    path('', illness_predictor_view, name="illness_predictor")
]

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from .views import illness_predictor_view, home, register, user_login, user_logout, get_patients_by_symptoms, get_patients_by_disease, get_symptoms_by_prediction_id, get_symptoms_by_disease, get_diseases_by_symptoms, get_diseases_by_prediction_id, get_prediction_by_id
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', home, name="home"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("predict/", illness_predictor_view, name="illness_predictor"),
    path("logout/", user_logout, name="logout"),
    path("admin/", admin.site.urls),
    path('patients/symptoms/', get_patients_by_symptoms, name='get_patients_by_symptoms'),
    path('patients/diseases/', get_patients_by_disease, name='get_patients_by_disease'),
    path('symptoms/', get_symptoms_by_disease, name='get_symptoms_by_disease'),
    path('symptoms/prediction/', get_symptoms_by_prediction_id, name='get_symptoms_by_prediction_id'),
    path('diseases/', get_diseases_by_symptoms, name='get_diseases_by_symptoms'),
    path('diseases/prediction/', get_diseases_by_prediction_id, name='get_diseases_by_prediction_id'),
    path('predict/<int:prediction_id>/', get_prediction_by_id, name='get_prediction_by_id'),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

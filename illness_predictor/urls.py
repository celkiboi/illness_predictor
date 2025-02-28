from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from .views import illness_predictor_view, home, register, user_login, user_logout, GetPatientsBySymptoms, GetPatientsByDisease, GetSymptomsByPredictionId, GetSymptomsByDisease, GetDiseasesBySymptoms, GetDiseasesByPredictionId, GetPredictionById
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', home, name="home"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("predict/", illness_predictor_view, name="illness_predictor"),
    path("logout/", user_logout, name="logout"),
    path("admin/", admin.site.urls),
    path('patients/symptoms/', GetPatientsBySymptoms.as_view(), name='get_patients_by_symptoms'),
    path('patients/diseases/', GetPatientsByDisease.as_view(), name='get_patients_by_disease'),
    path('symptoms/', GetSymptomsByDisease.as_view(), name='get_symptoms_by_disease'),
    path('symptoms/prediction/', GetSymptomsByPredictionId.as_view(), name='get_symptoms_by_prediction_id'),
    path('diseases/', GetDiseasesBySymptoms.as_view(), name='get_diseases_by_symptoms'),
    path('diseases/prediction/', GetDiseasesByPredictionId.as_view(), name='get_diseases_by_prediction_id'),
    path('predict/<int:prediction_id>/', GetPredictionById.as_view(), name='get_prediction_by_id'),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

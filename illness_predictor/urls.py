from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from .views import illness_predictor_view, home, register, user_login, user_logout
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', home, name="home"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("predict/", illness_predictor_view, name="illness_predictor"),
    path("logout/", user_logout, name="logout"),
    path("admin/", admin.site.urls),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

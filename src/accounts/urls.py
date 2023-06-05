from rest_framework import routers
from django.urls import path, include

from . import views


router = routers.DefaultRouter()
router.register(r'account', views.UserViewSet)


urlpatterns = [
    path('register-user', views.register_user, name='register-user'),
    path('register-vendor', views.register_vendor, name='register-vendor'),

    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('dashboard', views.dashboard, name='dashboard'),

    path('api/v1/', include(router.urls)),
]

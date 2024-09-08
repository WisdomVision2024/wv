"""
URL configuration for wv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from rest_framework.routers import DefaultRouter
from app import views

router = DefaultRouter()
router.register('user', views.userdataViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('',views.hello),
    path('login/', views.login_view),
    path('signup/',views.register_view),
    path('focus/',views.focus_view),
    path('continue/',views.continue_view),
    path('help/',views.help_view),
    path('unity/',views.unity_view,name='unity_view'),
    path('unity2/',views.unity2_view),
    path('getunity/',views.get_unity),
    path('gemini/',views.gemini_view),
    path('object/',views.object_view),


]



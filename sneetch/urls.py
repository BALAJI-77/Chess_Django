"""sneetch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
import django.contrib.auth.views

urlpatterns = [
    path('', include('games.urls')),
    path('admin/', admin.site.urls),
    path(r'accounts/logout/', django.contrib.auth.views.LogoutView.as_view()),
    path('accounts/', include('allauth.urls')),
    path('chess_ai/', include('chess_ai.urls')),
    path('profile/', include('games.urls')),
]

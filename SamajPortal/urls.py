"""
URL configuration for SamajPortal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from directory import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.smart_login, name='home'),
    path('update-member/<int:id>/', views.update_member, name='update_member'),
    path('register/', views.register, name='register'),
    path('save-member/', views.save_member, name='register_member'), # <-- Yeh line add karo
    path('directory-list/', views.directory_view, name='directory_view'),
    path('profile/<int:id>/', views.profile_view, name='profile_view'),
    path('edit/<int:member_id>/', views.edit_profile, name='edit_profile'),
]

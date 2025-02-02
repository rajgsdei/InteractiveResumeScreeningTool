from django.contrib import admin
from django.urls import path
from resume_screening import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
]

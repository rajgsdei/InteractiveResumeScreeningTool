from django.contrib import admin
from django.urls import path

from resume_screening.views import views
from resume_screening.views.chat_views import chat_assistant, chatbot_query
from resume_screening.views.landing_page import home, dashboard_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('view-resumes/', views.view_resumes, name='view-resumes'),
    path('about/', views.about, name='about'),
    path('extract-resume-data/', views.extract_resume_data_from_files, name='extract_resume_data'),
    path('chat-assistant/', chat_assistant, name='chat-assistant'),
    path('chatbot_query/', chatbot_query, name='chatbot_query'),
    path('candidate-profile/<uuid:resume_id>/', views.candidate_profile, name='candidate_profile'),
    path('api/dashboard-data/', dashboard_data, name='dashboard_data'),
]


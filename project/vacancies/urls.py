from django.urls import path
from . import views

app_name = 'vacancies'

urlpatterns = [
    path('latest-vacancies/', views.latest_vacancies, name='latest_vacancies'),
]
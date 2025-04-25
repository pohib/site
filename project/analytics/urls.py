from django.urls import path
from . import views

urlpatterns = [
    path('general-stats/', views.general_stats, name='general_stats'),
    path('demand/', views.demand, name='demand'),
    path('geography/', views.geography, name='geography'),
    path('skills/', views.skills, name='skills'),
]
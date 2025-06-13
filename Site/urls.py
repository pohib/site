from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from analytics import views as analytics_views
from vacancies import views as vacancies_views
from core.views import contact_view

urlpatterns = [
    path('admin/', admin.site.urls),
   
    path('general-stats/', analytics_views.general_stats, name='general_stats'),
    path('demand/', analytics_views.demand, name='demand'),
    path('geography/', analytics_views.geography, name='geography'),
    path('skills/', analytics_views.skills, name='skills'),
    path('latest/', vacancies_views.latest_vacancies, name='latest'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('contact/', contact_view, name='contact'),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
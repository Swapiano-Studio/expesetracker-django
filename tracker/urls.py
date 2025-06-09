from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('guest-dashboard/', views.guest_dashboard, name='guest_dashboard'),
    path('about/', views.about, name='about'),
    path('export-csv/', views.export_expenses_csv, name='export_expenses_csv'),
]

from django.urls import path
from .views import dashboard_view, equipment_list_view, get_equipment_info

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('equipment/', equipment_list_view, name='equipment_list'),
        path('api/equipment/<int:pk>/', get_equipment_info, name='equipment_info'),  # <-- Новый путь
]
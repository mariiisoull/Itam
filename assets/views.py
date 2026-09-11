from django.shortcuts import render
from django.utils import timezone
from django.db import models
from .models import Equipment, Cabinet, EquipmentHistory



from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def dashboard_view(request):
    current_year = timezone.now().year
    
    all_equipment = Equipment.objects.all()
    total_count = all_equipment.count()
    
    new_count = all_equipment.filter(year_manufactured__gte=current_year - 3).count()
    old_count = total_count - new_count
    
    cabinets_count = Cabinet.objects.count()
    
    recent_history = EquipmentHistory.objects.select_related('equipment', 'old_cabinet', 'new_cabinet')[:5]
    
    context = {
        'total_count': total_count,
        'new_count': new_count,
        'old_count': old_count,
        'cabinets_count': cabinets_count,
        'recent_history': recent_history,
    }
    
    return render(request, 'assets/dashboard.html', context)


def equipment_list_view(request):
    query = request.GET.get('q', '')
    cabinet_id = request.GET.get('cabinet', '')
    
    equipment_list = Equipment.objects.select_related('current_cabinet', 'current_user').all()

    if query:
        equipment_list = equipment_list.filter(
            models.Q(name__icontains=query) | models.Q(serial_number__icontains=query)
        )
    
    if cabinet_id:
        equipment_list = equipment_list.filter(current_cabinet_id=cabinet_id)

    cabinets = Cabinet.objects.all()

    context = {
        'equipment_list': equipment_list,
        'cabinets': cabinets,
        'query': query,
        'selected_cabinet': cabinet_id,
    }
    return render(request, 'assets/equipment_list.html', context)




def get_equipment_info(request, pk):
    """Возвращает текущий кабинет и пользователя для выбранной техники в формате JSON"""
    equipment = get_object_or_404(Equipment, pk=pk)
    data = {
        'cabinet_id': equipment.current_cabinet.id if equipment.current_cabinet else '',
        'user_id': equipment.current_user.id if equipment.current_user else '',
    }
    return JsonResponse(data)
from django.contrib import admin
from .models import Cabinet, Employee, Equipment, EquipmentHistory


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ('number', 'floor')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position')


@admin.register(EquipmentHistory)
class EquipmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'old_cabinet', 'new_cabinet', 'old_user', 'new_user', 'change_date')
    readonly_fields = ('change_date',)

    # Подключаем JS-скрипт для автоподстановки текущих кабинета и пользователя при выборе техники
    class Media:
        js = ('assets/js/auto_fill_history.js',)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment_type', 'serial_number', 'year_manufactured', 'status', 'current_cabinet', 'current_user')
    list_filter = ('equipment_type', 'status', 'year_manufactured', 'current_cabinet')
    search_fields = ('name', 'serial_number')

    # Выводим подсказку в форме редактирования
    readonly_fields = ('get_current_info_display',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'equipment_type', 'serial_number', 'year_manufactured', 'status')
        }),
        ('Текущее местоположение и ответственный (Заполняется при перемещении)', {
            'fields': ('get_current_info_display', 'current_cabinet', 'current_user'),
            'description': 'В поле "Текущее состояние" отображается, где техника находится СЕЙЧАС. Ниже выберите новые значения для перемещения.'
        }),
    )

    def get_current_info_display(self, obj):
        if obj.pk:
            cab = obj.current_cabinet.number if obj.current_cabinet else "Не назначен"
            usr = obj.current_user.full_name if obj.current_user else "Не назначен"
            return f"Сейчас в кабинете: {cab} | Ответственный: {usr}"
        return "Новое оборудование (еще не сохранено)"
    
    get_current_info_display.short_description = "Текущее состояние в базе"

    def save_model(self, request, obj, form, change):
        if change:
            # Берем актуальные данные из БД ДО сохранения новых
            old_obj = Equipment.objects.get(pk=obj.pk)
            
            cabinet_changed = old_obj.current_cabinet != obj.current_cabinet
            user_changed = old_obj.current_user != obj.current_user

            # Записываем в историю старый и новый кабинет/пользователь
            if cabinet_changed or user_changed:
                EquipmentHistory.objects.create(
                    equipment=obj,
                    old_cabinet=old_obj.current_cabinet,
                    new_cabinet=obj.current_cabinet,
                    old_user=old_obj.current_user,
                    new_user=obj.current_user,
                    comment="Автоматическая запись перемещения"
                )

        super().save_model(request, obj, form, change)
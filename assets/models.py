from django.db import models
from django.utils import timezone

class Cabinet(models.Model):
    """Модель кабинета"""
    number = models.CharField("Номер / Название кабинета", max_length=50)
    floor = models.IntegerField("Этаж", default=1)

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"

    def __str__(self):
        return f"Каб. {self.number} (этаж {self.floor})"


class Employee(models.Model):
    """Модель сотрудника / пользователя техники"""
    full_name = models.CharField("ФИО сотрудника", max_length=150)
    position = models.CharField("Должность", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.full_name


class Equipment(models.Model):
    STATUS_CHOICES = [
        ('in_use', 'В эксплуатации'),
        ('in_stock', 'На складе'),
        ('repair', 'В ремонте'),
        ('written_off', 'Списано'),
    ]

    TYPE_CHOICES = [
        ('pc', 'Компьютер / ПК'),
        ('laptop', 'Ноутбук'),
        ('monitor', 'Монитор'),
        ('printer', 'МФУ / Принтер'),
        ('other', 'Другое оборудование'),
    ]

    name = models.CharField("Наименование техники", max_length=150)
    
    equipment_type = models.CharField(
        "Тип техники", 
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='pc'
    )
    
    serial_number = models.CharField("Инвентарный / Серийный номер", max_length=100, unique=True)
    year_manufactured = models.IntegerField("Год выпуска")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='in_use')
    
    current_cabinet = models.ForeignKey(Cabinet, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Текущий кабинет")
    current_user = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Текущий пользователь")

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    @property
    def is_new(self):
        """Определяем, считается ли техника новой (выпущенной за последние 3 года)"""
        current_year = timezone.now().year
        return (current_year - self.year_manufactured) <= 3


class EquipmentHistory(models.Model):
    """История перемещений и смены пользователей"""
    equipment = models.ForeignKey(
        Equipment, 
        on_delete=models.CASCADE, 
        related_name='history', 
        verbose_name="Техника"
    )
    old_cabinet = models.ForeignKey(
        Cabinet, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='+', 
        verbose_name="Старый кабинет"
    )
    new_cabinet = models.ForeignKey(
        Cabinet, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='+', 
        verbose_name="Новый кабинет"
    )
    old_user = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='+', 
        verbose_name="Старый пользователь"
    )
    new_user = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='+', 
        verbose_name="Новый пользователь"
    )
    change_date = models.DateTimeField("Дата изменения", auto_now_add=True)
    comment = models.TextField("Примечание", blank=True, null=True)

    class Meta:
        verbose_name = "Запись истории"
        verbose_name_plural = "История перемещений"

    def __str__(self):
        return f"Перемещение {self.equipment} от {self.change_date}"

    def save(self, *args, **kwargs):
        # 1. Сначала сохраняем саму запись истории перемещения
        super().save(*args, **kwargs)
        
        # 2. Гарантированно обновляем текущий кабинет и пользователя у привязанной техники в БД
        if self.equipment_id:
            Equipment.objects.filter(id=self.equipment_id).update(
                current_cabinet=self.new_cabinet,
                current_user=self.new_user
            )
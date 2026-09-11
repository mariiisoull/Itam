window.addEventListener('DOMContentLoaded', function() {
    const equipmentSelect = document.getElementById('id_equipment');
    const oldCabinetSelect = document.getElementById('id_old_cabinet');
    const oldUserSelect = document.getElementById('id_old_user');

    if (equipmentSelect) {
        equipmentSelect.addEventListener('change', function() {
            const equipmentId = this.value;
            if (!equipmentId) return;

            // Запрашиваем данные о выбранной технике
            fetch(`/api/equipment/${equipmentId}/`)
                .then(response => response.json())
                .then(data => {
                    if (oldCabinetSelect && data.cabinet_id) {
                        oldCabinetSelect.value = data.cabinet_id;
                    }
                    if (oldUserSelect && data.user_id) {
                        oldUserSelect.value = data.user_id;
                    }
                })
                .catch(error => console.error('Ошибка получения данных:', error));
        });
    }
});
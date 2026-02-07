const Filters = (() => {
    function initRadioFilters() {
        const checkboxes = document.querySelectorAll('#radio-filters input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                TowerMap.setRadioVisible(cb.value, cb.checked);
            });
        });
    }

    function initOperatorFilter() {
        const select = document.getElementById('operator-filter');
        select.addEventListener('change', () => {
            TowerMap.filterByOperator(select.value);
        });
    }

    function updateOperatorDropdown() {
        const select = document.getElementById('operator-filter');
        const operators = TowerMap.getUniqueOperators();
        select.innerHTML = '<option value="">All Operators</option>';
        operators.forEach(op => {
            const option = document.createElement('option');
            option.value = op;
            option.textContent = op;
            select.appendChild(option);
        });
    }

    return { initRadioFilters, initOperatorFilter, updateOperatorDropdown };
})();

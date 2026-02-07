document.addEventListener('DOMContentLoaded', () => {
    TowerMap.init();
    Filters.initRadioFilters();
    Filters.initOperatorFilter();
    loadStatus();

    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const radiusSlider = document.getElementById('radius-slider');
    const radiusValue = document.getElementById('radius-value');
    const resultsInfo = document.getElementById('results-info');

    radiusSlider.addEventListener('input', () => {
        radiusValue.textContent = radiusSlider.value;
    });

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') performSearch();
    });

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        const radius = parseInt(radiusSlider.value);
        setLoading(true);
        resultsInfo.innerHTML = 'Searching...';

        try {
            const location = await Search.resolve(query);
            const result = await Search.searchTowers(location.lat, location.lon, radius);

            TowerMap.plotTowers(result.towers);
            TowerMap.showSearchArea(location.lat, location.lon, radius);
            Filters.updateOperatorDropdown();

            let info = `<span class="count">${result.count}</span> towers found`;
            if (result.cached) info += ' (cached)';
            if (result.rate_limited) info += '<br><span style="color:#ff9933">Rate limited — showing cached data</span>';
            if (result.message) info += `<br><span style="color:#ffcc00">${result.message}</span>`;
            resultsInfo.innerHTML = info;

            loadStatus();
        } catch (err) {
            resultsInfo.innerHTML = `<span class="error-msg">${err.message}</span>`;
            setStatus('error', 'Error');
        } finally {
            setLoading(false);
        }
    }

    function setLoading(loading) {
        searchBtn.disabled = loading;
        searchBtn.textContent = loading ? 'Searching...' : 'Search Towers';
        const dot = document.querySelector('.status-dot');
        if (loading) {
            dot.classList.add('loading');
            document.getElementById('status-text').textContent = 'Searching...';
        } else {
            dot.classList.remove('loading');
            document.getElementById('status-text').textContent = 'Ready';
        }
    }

    function setStatus(state, text) {
        const dot = document.querySelector('.status-dot');
        dot.classList.remove('loading', 'error');
        if (state === 'error') dot.classList.add('error');
        document.getElementById('status-text').textContent = text;
    }

    async function loadStatus() {
        try {
            const resp = await fetch('/api/status');
            const data = await resp.json();
            document.getElementById('api-calls').textContent = data.api_calls_today;
            document.getElementById('api-limit').textContent = data.api_daily_limit;
            document.getElementById('db-total').textContent = data.total_towers;
        } catch (e) {
            // silently fail
        }
    }
});

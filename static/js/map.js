const TowerMap = (() => {
    const RADIO_COLORS = {
        GSM:  '#ffcc00',
        LTE:  '#3399ff',
        NR:   '#9933ff',
        CDMA: '#ff9933',
        UMTS: '#33cccc',
    };

    let map;
    let markerLayers = {};   // radio type -> L.layerGroup
    let allTowers = [];
    let searchCircle = null;

    function init() {
        map = L.map('map', {
            center: [39.8, -98.5],
            zoom: 5,
            zoomControl: true,
        });

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://carto.com/">CARTO</a> | &copy; <a href="https://www.openstreetmap.org/">OSM</a>',
            subdomains: 'abcd',
            maxZoom: 19,
        }).addTo(map);

        // Create a layer group per radio type
        Object.keys(RADIO_COLORS).forEach(radio => {
            markerLayers[radio] = L.layerGroup().addTo(map);
        });
    }

    function clearMarkers() {
        Object.values(markerLayers).forEach(lg => lg.clearLayers());
        allTowers = [];
    }

    function plotTowers(towers) {
        clearMarkers();
        allTowers = towers;

        towers.forEach(t => {
            const color = RADIO_COLORS[t.radio] || '#888888';
            const layer = markerLayers[t.radio];
            if (!layer) return;

            const marker = L.circleMarker([t.lat, t.lon], {
                radius: 6,
                fillColor: color,
                fillOpacity: 0.85,
                color: color,
                weight: 1,
                opacity: 0.6,
            });

            marker.bindPopup(_buildPopup(t));
            marker.towerData = t;
            layer.addLayer(marker);
        });
    }

    function _buildPopup(t) {
        const rows = [
            ['Radio', t.radio],
            ['Operator', t.operator || 'Unknown'],
            ['Cell ID', t.cell_id],
            ['LAC', t.lac],
            ['MCC/MNC', `${t.mcc}/${t.mnc}`],
            ['Range', t.range_m ? `${t.range_m}m` : '-'],
            ['Signal', t.signal_avg ? `${t.signal_avg} dBm` : '-'],
            ['Samples', t.samples || '-'],
            ['Source', t.source],
        ];

        const rowsHtml = rows.map(([label, value]) =>
            `<div class="popup-row"><span class="popup-label">${label}</span><span class="popup-value">${value}</span></div>`
        ).join('');

        return `<div class="popup-title">${t.radio} Tower</div>${rowsHtml}`;
    }

    function setRadioVisible(radio, visible) {
        const layer = markerLayers[radio];
        if (!layer) return;
        if (visible) {
            map.addLayer(layer);
        } else {
            map.removeLayer(layer);
        }
    }

    function showSearchArea(lat, lon, radiusKm) {
        if (searchCircle) {
            map.removeLayer(searchCircle);
        }
        searchCircle = L.circle([lat, lon], {
            radius: radiusKm * 1000,
            color: '#00cc66',
            fillColor: '#00cc66',
            fillOpacity: 0.05,
            weight: 1,
            dashArray: '5,5',
        }).addTo(map);

        map.fitBounds(searchCircle.getBounds(), { padding: [20, 20] });
    }

    function panTo(lat, lon, zoom) {
        map.setView([lat, lon], zoom || 13);
    }

    function filterByOperator(operator) {
        Object.values(markerLayers).forEach(lg => {
            lg.eachLayer(marker => {
                if (!operator || (marker.towerData && marker.towerData.operator === operator)) {
                    marker.setStyle({ fillOpacity: 0.85, opacity: 0.6 });
                } else {
                    marker.setStyle({ fillOpacity: 0.1, opacity: 0.1 });
                }
            });
        });
    }

    function getUniqueOperators() {
        const ops = new Set();
        allTowers.forEach(t => {
            if (t.operator) ops.add(t.operator);
        });
        return Array.from(ops).sort();
    }

    return {
        init, clearMarkers, plotTowers, setRadioVisible,
        showSearchArea, panTo, filterByOperator, getUniqueOperators,
        RADIO_COLORS,
    };
})();

const Search = (() => {
    const COORD_REGEX = /^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/;

    async function resolve(query) {
        const match = query.trim().match(COORD_REGEX);
        if (match) {
            return {
                lat: parseFloat(match[1]),
                lon: parseFloat(match[2]),
                label: `${match[1]}, ${match[2]}`,
            };
        }
        return await geocode(query);
    }

    async function geocode(query) {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1&countrycodes=us`;
        const resp = await fetch(url, {
            headers: { 'User-Agent': 'RFTowerMapper/1.0' },
        });
        if (!resp.ok) throw new Error('Geocoding failed');
        const results = await resp.json();
        if (results.length === 0) throw new Error('Location not found');
        return {
            lat: parseFloat(results[0].lat),
            lon: parseFloat(results[0].lon),
            label: results[0].display_name,
        };
    }

    async function searchTowers(lat, lon, radiusKm) {
        const resp = await fetch('/api/towers/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat, lon, radius: radiusKm }),
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || 'Search failed');
        }
        return await resp.json();
    }

    return { resolve, searchTowers };
})();

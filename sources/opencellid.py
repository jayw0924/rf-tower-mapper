import math
import requests
from datetime import datetime, timedelta
from core.models import db, CellTower, ApiUsage
import config

# OpenCelliD limits BBOX to 4,000,000 sq meters (~2km x 2km)
# We tile larger search areas into ~1.5km grid cells
TILE_SIZE_KM = 1.5


def search_area(lat, lon, radius_km):
    """Search for cell towers in an area. Returns cached data or fetches from API."""
    cached = _get_cached(lat, lon, radius_km)
    cache_fresh = _is_cache_fresh(lat, lon, radius_km)

    if cache_fresh and cached:
        return {
            'towers': [t.to_dict() for t in cached],
            'count': len(cached),
            'cached': True,
            'rate_limited': False,
        }

    if not config.OPENCELLID_API_KEY:
        return {
            'towers': [t.to_dict() for t in cached],
            'count': len(cached),
            'cached': True,
            'rate_limited': False,
            'message': 'No API key configured — showing cached data only',
        }

    if not ApiUsage.can_call(config.OPENCELLID_DAILY_LIMIT):
        return {
            'towers': [t.to_dict() for t in cached],
            'count': len(cached),
            'cached': True,
            'rate_limited': True,
        }

    towers_data, api_calls = _fetch_tiled(lat, lon, radius_km)

    for _ in range(api_calls):
        ApiUsage.increment()

    if towers_data:
        _upsert_towers(towers_data)

    fresh = _get_cached(lat, lon, radius_km)
    return {
        'towers': [t.to_dict() for t in fresh],
        'count': len(fresh),
        'cached': False,
        'rate_limited': False,
    }


def _fetch_tiled(lat, lon, radius_km):
    """Tile the search area into small BBOX queries that fit the 4km² limit."""
    delta_lat = radius_km / 111.0
    cos_lat = max(abs(math.cos(math.radians(lat))), 0.01)
    delta_lon = radius_km / (111.0 * cos_lat)

    lat_min = lat - delta_lat
    lat_max = lat + delta_lat
    lon_min = lon - delta_lon
    lon_max = lon + delta_lon

    tile_deg = TILE_SIZE_KM / 111.0
    tile_deg_lon = TILE_SIZE_KM / (111.0 * cos_lat)

    all_cells = []
    api_calls = 0
    seen = set()

    cur_lat = lat_min
    while cur_lat < lat_max:
        cur_lon = lon_min
        while cur_lon < lon_max:
            if not ApiUsage.can_call(config.OPENCELLID_DAILY_LIMIT):
                return all_cells, api_calls

            t_lat_max = min(cur_lat + tile_deg, lat_max)
            t_lon_max = min(cur_lon + tile_deg_lon, lon_max)

            bbox = f"{cur_lat:.6f},{cur_lon:.6f},{t_lat_max:.6f},{t_lon_max:.6f}"
            cells = _fetch_bbox(bbox)
            api_calls += 1

            if cells:
                for c in cells:
                    key = (c.get('cellid'), c.get('lac'), c.get('mcc'),
                           c.get('mnc'), c.get('radio'))
                    if key not in seen:
                        seen.add(key)
                        all_cells.append(c)

            cur_lon += tile_deg_lon
        cur_lat += tile_deg

    return all_cells, api_calls


def _fetch_bbox(bbox):
    """Fetch towers for a single BBOX tile."""
    try:
        resp = requests.get(
            f'{config.OPENCELLID_BASE_URL}/getInArea',
            params={
                'key': config.OPENCELLID_API_KEY,
                'BBOX': bbox,
                'format': 'json',
                'limit': 1000,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            if 'cells' in data:
                return data['cells']
        return []
    except requests.RequestException:
        return []


def _upsert_towers(towers_data):
    """Insert or update towers from API response."""
    for cell in towers_data:
        existing = CellTower.query.filter_by(
            cell_id=cell.get('cellid', 0),
            lac=cell.get('lac', 0),
            mcc=cell.get('mcc', 0),
            mnc=cell.get('mnc', 0),
            radio=cell.get('radio', 'GSM'),
        ).first()

        if existing:
            existing.lat = cell.get('lat', existing.lat)
            existing.lon = cell.get('lon', existing.lon)
            existing.range_m = cell.get('range', existing.range_m)
            existing.signal_avg = cell.get('averageSignalStrength', existing.signal_avg)
            existing.samples = cell.get('samples', existing.samples)
            existing.updated_at = datetime.utcnow()
        else:
            tower = CellTower(
                cell_id=cell.get('cellid', 0),
                lac=cell.get('lac', 0),
                mcc=cell.get('mcc', 0),
                mnc=cell.get('mnc', 0),
                lat=cell.get('lat', 0),
                lon=cell.get('lon', 0),
                radio=cell.get('radio', 'GSM'),
                range_m=cell.get('range'),
                signal_avg=cell.get('averageSignalStrength'),
                samples=cell.get('samples'),
                source='opencellid',
            )
            db.session.add(tower)

    db.session.commit()


def _get_cached(lat, lon, radius_km):
    """Get towers from DB within bounding box."""
    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (111.0 * max(abs(math.cos(math.radians(lat))), 0.01))

    return CellTower.query.filter(
        CellTower.lat.between(lat - delta_lat, lat + delta_lat),
        CellTower.lon.between(lon - delta_lon, lon + delta_lon),
    ).all()


def _is_cache_fresh(lat, lon, radius_km):
    """Check if we have recent data for this area."""
    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (111.0 * max(abs(math.cos(math.radians(lat))), 0.01))
    cutoff = datetime.utcnow() - timedelta(hours=config.OPENCELLID_CACHE_HOURS)

    recent = CellTower.query.filter(
        CellTower.lat.between(lat - delta_lat, lat + delta_lat),
        CellTower.lon.between(lon - delta_lon, lon + delta_lon),
        CellTower.updated_at >= cutoff,
    ).first()

    return recent is not None

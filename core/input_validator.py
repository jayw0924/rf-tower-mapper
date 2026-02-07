import re


def validate_lat(lat):
    try:
        lat = float(lat)
    except (TypeError, ValueError):
        return None, 'Invalid latitude'
    if lat < -90 or lat > 90:
        return None, 'Latitude must be between -90 and 90'
    return lat, None


def validate_lon(lon):
    try:
        lon = float(lon)
    except (TypeError, ValueError):
        return None, 'Invalid longitude'
    if lon < -180 or lon > 180:
        return None, 'Longitude must be between -180 and 180'
    return lon, None


def validate_radius(radius, min_km=1, max_km=50):
    try:
        radius = float(radius)
    except (TypeError, ValueError):
        return None, 'Invalid radius'
    if radius < min_km or radius > max_km:
        return None, f'Radius must be between {min_km} and {max_km} km'
    return radius, None


def sanitize_address(address):
    if not address or not isinstance(address, str):
        return None, 'Address is required'
    address = address.strip()
    if len(address) > 200:
        return None, 'Address too long (max 200 chars)'
    address = re.sub(r'[^\w\s,.\-#/]', '', address)
    if not address:
        return None, 'Address contains no valid characters'
    return address, None


def validate_search_params(data):
    errors = []
    lat, err = validate_lat(data.get('lat'))
    if err:
        errors.append(err)
    lon, err = validate_lon(data.get('lon'))
    if err:
        errors.append(err)
    radius = data.get('radius', 10)
    radius, err = validate_radius(radius)
    if err:
        errors.append(err)
    if errors:
        return None, errors
    return {'lat': lat, 'lon': lon, 'radius_km': radius}, None

import urllib.request, urllib.parse, json, logging
logger = logging.getLogger(__name__)
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
HEADERS = {'User-Agent': 'EventNest/1.0'}

def geocode(address):
    if not address or not address.strip():
        return None
    query = urllib.parse.urlencode({'q': address, 'format': 'json', 'limit': 1})
    req = urllib.request.Request(f'{NOMINATIM_URL}?{query}', headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as exc:
        logger.warning(f'Geocode failed for "{address}": {exc}')
    return None

def ensure_geocoded(event):
    if event.latitude and event.longitude:
        return event
    if not (event.address or event.city):
        return event
    query = ', '.join(filter(None, [event.venue, event.address, event.city]))
    result = geocode(query)
    if result:
        event.latitude, event.longitude = result
        event.save(update_fields=['latitude', 'longitude'])
    return event

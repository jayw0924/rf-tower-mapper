# RF Tower Mapper

Flask web dashboard for geospatial mapping of US cell towers and RF transmitters. Uses OpenCelliD as the primary data source with a Leaflet.js dark-themed interactive map.

![Port](https://img.shields.io/badge/port-5001-green) ![Python](https://img.shields.io/badge/python-3-blue)

## Features

- Interactive dark map (CartoDB Dark Matter tiles) with color-coded tower markers
- Search by city/address (geocoded via Nominatim) or direct `lat,lon` coordinates
- Adjustable search radius (1–50 km), tiled into API-compatible BBOX queries
- Filter by radio type: GSM, LTE, NR (5G), CDMA, UMTS
- Filter by operator
- Click any tower for details: radio, cell ID, LAC, MCC/MNC, range, signal strength
- SQLite cache with 24-hour freshness — avoids redundant API calls
- Rate limit tracking (1,000 calls/day)
- Runs as a systemd service on boot

## Radio Type Colors

| Type | Color | Description |
|------|-------|-------------|
| GSM  | Yellow | 2G |
| LTE  | Blue | 4G |
| NR   | Purple | 5G |
| CDMA | Orange | 2G/3G |
| UMTS | Teal | 3G |

## Setup

```bash
cd ~/dev/projects/rf-tower-mapper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Get a free API key from [OpenCelliD](https://opencellid.org) (email registration required).

Set the key as an environment variable:

```bash
export OPENCELLID_API_KEY=pk.your_key_here
```

Or for the systemd service:

```bash
sudo systemctl edit rf-tower-mapper
# Add under [Service]:
# Environment=OPENCELLID_API_KEY=pk.your_key_here
sudo systemctl restart rf-tower-mapper
```

The app works without an API key (empty results) but won't fetch live data until one is configured.

## Usage

### Run manually

```bash
source venv/bin/activate
python app.py
# Serves at http://localhost:5001
```

### Systemd service

```bash
sudo systemctl start rf-tower-mapper
sudo systemctl status rf-tower-mapper
sudo journalctl -u rf-tower-mapper -f
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Map page |
| POST | `/api/towers/search` | Search towers by lat/lon/radius |
| GET | `/api/towers/<id>` | Single tower detail |
| GET | `/api/status` | API usage + DB stats |

### Search request

```json
POST /api/towers/search
{"lat": 40.753, "lon": -73.985, "radius": 2}
```

### Search response

```json
{
  "towers": [{"id", "cell_id", "lac", "mcc", "mnc", "lat", "lon", "radio", "range_m", "signal_avg", "operator", "samples", "source"}],
  "count": 447,
  "cached": true,
  "rate_limited": false
}
```

## API Rate Limits

OpenCelliD allows 1,000 requests/day on the free tier. Each request covers a ~1.5 km tile (limited to 4 km² per BBOX query). Larger search radii consume more API calls:

| Radius | Approx. API calls |
|--------|-------------------|
| 2 km   | ~11 |
| 5 km   | ~50 |
| 10 km  | ~180 |
| 50 km  | ~4,400 (exceeds daily limit) |

Results are cached in SQLite for 24 hours, so repeat searches are free.

## Project Structure

```
rf-tower-mapper/
├── app.py                  # Flask entry point (port 5001)
├── config.py               # Settings, API keys, paths
├── requirements.txt
├── core/
│   ├── models.py           # SQLAlchemy models: CellTower, ApiUsage
│   └── input_validator.py  # Coordinate/radius/string validation
├── sources/
│   ├── opencellid.py       # OpenCelliD API client + BBOX tiling + caching
│   ├── hifld.py            # HIFLD government towers (Phase 2)
│   └── fcc_uls.py          # FCC ULS transmitters (Phase 2)
├── data/                   # Runtime data (SQLite DB)
├── static/
│   ├── css/style.css
│   └── js/
│       ├── app.js          # Main orchestrator
│       ├── map.js          # Leaflet map, markers, layers
│       ├── search.js       # Geocoding + coordinate search
│       └── filters.js      # Radio type/operator filters
└── templates/
    ├── base.html
    └── index.html
```

## Roadmap

- **Phase 2:** HIFLD government tower data, FCC ULS licensed transmitters, coverage radius overlays, heatmap mode
- **Phase 3:** Bulk CSV import, export to CSV/JSON, saved locations, distance measurement, statistics page

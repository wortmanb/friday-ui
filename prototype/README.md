# Friday UI v2 • D3 Dashboard Prototype

This prototype replaces the v1 cat avatar with a D3-based dashboard focused on real, reliable data in a minimal footprint.

## Why this over the v1 cat avatar?
- **More useful**: surfaces real system metrics and service health instead of a decorative avatar.
- **Smaller footprint**: compact widget designed for a screen corner.
- **More reliable**: polling-based updates with graceful offline state.

## What it shows (Option B: Homelab metrics)
- CPU usage (sparkline)
- Memory usage (sparkline)
- Disk usage (donut)
- Load averages (bars)
- Optional service health checks

## Run it

```bash
python3 prototype/server.py
```

Then open:
- `http://127.0.0.1:8765/` for live metrics
- `http://127.0.0.1:8765/demo.html` for demo mode

## Configure service checks

Set `FRIDAY_SERVICES` to a comma-separated list of `name=url` pairs.

```bash
export FRIDAY_SERVICES="elasticsearch=http://localhost:9200,k8s-api=https://localhost:6443/healthz"
python3 prototype/server.py
```

## Notes
- Uses only the Python standard library (no extra dependencies).
- Polling interval is 5 seconds by default.
- D3.js is loaded from a CDN for the prototype.

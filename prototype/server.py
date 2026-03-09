#!/usr/bin/env python3
"""Minimal dashboard backend for Friday UI prototype.

- Serves static files from ./static
- Provides /api/metrics JSON endpoint

Standard library only.
"""

import json
import os
import platform
import time
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from shutil import disk_usage


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class MetricsCollector:
    def __init__(self):
        self._last_cpu = None
        self._last_cpu_ts = None

    def _read_proc_stat(self):
        try:
            with open("/proc/stat", "r", encoding="utf-8") as handle:
                first = handle.readline().strip().split()
            if not first or first[0] != "cpu":
                return None
            values = [int(v) for v in first[1:]]
            total = sum(values)
            idle = values[3] + values[4] if len(values) > 4 else values[3]
            return total, idle
        except FileNotFoundError:
            return None

    def cpu_usage(self):
        sample = self._read_proc_stat()
        now = time.time()
        if sample is None:
            return None
        total, idle = sample
        if self._last_cpu is None:
            self._last_cpu = (total, idle)
            self._last_cpu_ts = now
            return None
        last_total, last_idle = self._last_cpu
        delta_total = total - last_total
        delta_idle = idle - last_idle
        self._last_cpu = (total, idle)
        self._last_cpu_ts = now
        if delta_total <= 0:
            return None
        usage = (delta_total - delta_idle) / delta_total
        return max(0.0, min(1.0, usage))

    def mem_usage(self):
        try:
            meminfo = {}
            with open("/proc/meminfo", "r", encoding="utf-8") as handle:
                for line in handle:
                    key, value = line.split(":", 1)
                    meminfo[key.strip()] = int(value.strip().split()[0])
            total_kb = meminfo.get("MemTotal", 0)
            avail_kb = meminfo.get("MemAvailable", 0)
            used_kb = total_kb - avail_kb
            usage = used_kb / total_kb if total_kb else 0.0
            return {
                "used_kb": used_kb,
                "total_kb": total_kb,
                "usage": usage,
            }
        except FileNotFoundError:
            return None

    def load_avg(self):
        try:
            with open("/proc/loadavg", "r", encoding="utf-8") as handle:
                parts = handle.read().strip().split()
            return {
                "1m": float(parts[0]),
                "5m": float(parts[1]),
                "15m": float(parts[2]),
            }
        except (FileNotFoundError, ValueError, IndexError):
            return None

    def uptime_sec(self):
        try:
            with open("/proc/uptime", "r", encoding="utf-8") as handle:
                return float(handle.read().strip().split()[0])
        except (FileNotFoundError, ValueError, IndexError):
            return None

    def disk(self):
        usage = disk_usage("/")
        used = usage.used
        total = usage.total
        return {
            "used_bytes": used,
            "total_bytes": total,
            "usage": used / total if total else 0.0,
        }

    def service_checks(self):
        services = []
        raw = os.getenv("FRIDAY_SERVICES", "").strip()
        if not raw:
            return services
        entries = [item for item in raw.split(",") if item]
        for entry in entries:
            if "=" not in entry:
                continue
            name, url = entry.split("=", 1)
            name = name.strip()
            url = url.strip()
            if not name or not url:
                continue
            start = time.time()
            ok = False
            status = None
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    status = resp.status
                ok = 200 <= status < 500
            except Exception:
                ok = False
            latency_ms = int((time.time() - start) * 1000)
            services.append(
                {
                    "name": name,
                    "url": url,
                    "ok": ok,
                    "status": status,
                    "latency_ms": latency_ms,
                }
            )
        return services

    def collect(self):
        return {
            "timestamp": time.time(),
            "host": platform.node(),
            "uptime_sec": self.uptime_sec(),
            "cpu": {"usage": self.cpu_usage()},
            "memory": self.mem_usage(),
            "disk": self.disk(),
            "load": self.load_avg(),
            "services": self.service_checks(),
        }


COLLECTOR = MetricsCollector()


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/metrics"):
            payload = COLLECTOR.collect()
            data = json.dumps(payload).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()


def main():
    host = os.getenv("FRIDAY_HOST", "127.0.0.1")
    port = int(os.getenv("FRIDAY_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"Friday UI prototype running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    os.chdir(STATIC_DIR)
    main()

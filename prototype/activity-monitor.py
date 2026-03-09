#!/usr/bin/env python3
"""Monitor OpenClaw activity and update Friday's state file.

Uses multiple signals to detect activity:
1. Session file modification times
2. Log file activity (chat.send events)
3. State file recency (for external updates)

States:
- IDLE: No recent activity
- WORKING: Active request processing detected
- THINKING: Very recent activity (processing in progress)
"""

import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from threading import Thread

STATE_FILE = Path.home() / ".friday-activity-state"
SESSIONS_FILE = Path.home() / ".openclaw/agents/main/sessions/sessions.json"
LOG_DIR = Path("/tmp/openclaw")

# Timing thresholds (seconds)
THINKING_THRESHOLD = 5    # Recent activity = THINKING
WORKING_THRESHOLD = 30    # Activity within this = WORKING
IDLE_THRESHOLD = 60       # No activity for this long = IDLE
POLL_INTERVAL = 2         # How often to check


def get_today_log():
    """Get path to today's log file."""
    today = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"openclaw-{today}.log"


def update_state(state, description):
    """Update Friday's activity state file."""
    # Check if state actually changed
    try:
        with open(STATE_FILE, 'r') as f:
            current = json.load(f)
            if current.get("state") == state.upper():
                return  # No change
    except (IOError, json.JSONDecodeError):
        pass
    
    data = {
        "state": state.upper(),
        "description": description,
        "timestamp": time.time()
    }
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] State: {state} - {description}")
    except IOError as e:
        print(f"Error updating state: {e}", file=sys.stderr)


def get_last_chat_send_time():
    """Get timestamp of last chat.send from log."""
    log_file = get_today_log()
    if not log_file.exists():
        return 0
    
    try:
        # Use tail + grep to efficiently find last chat.send
        result = subprocess.run(
            ['sh', '-c', f'tac "{log_file}" | grep -m1 "chat.send" | head -1'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            line = result.stdout.strip()
            data = json.loads(line)
            # Parse timestamp from log
            ts_str = data.get("_meta", {}).get("date", "")
            if ts_str:
                # Parse ISO format: 2026-03-09T19:15:16.166Z
                dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                return dt.timestamp()
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, KeyError):
        pass
    
    return 0


def get_session_file_mtime():
    """Get modification time of sessions.json."""
    if SESSIONS_FILE.exists():
        return SESSIONS_FILE.stat().st_mtime
    return 0


def check_openclaw_process_active():
    """Check if openclaw-tui or openclaw process is actively using CPU."""
    try:
        # Get CPU usage of openclaw processes
        result = subprocess.run(
            ['sh', '-c', 'ps aux | grep -E "openclaw-tui|openclaw-gateway" | grep -v grep | awk \'{sum += $3} END {print sum}\''],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            cpu = float(result.stdout.strip())
            return cpu > 1.0  # More than 1% CPU = active
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return False


def determine_state():
    """Determine current activity state based on multiple signals."""
    now = time.time()
    
    # Priority 1: Check if process is actively using CPU (real-time indicator)
    if check_openclaw_process_active():
        return ("WORKING", "Processing request...")
    
    # Priority 2: Check session file modification time
    session_mtime = get_session_file_mtime()
    session_age = now - session_mtime if session_mtime else float('inf')
    
    # Priority 3: Check last chat.send event
    last_chat = get_last_chat_send_time()
    chat_age = now - last_chat if last_chat else float('inf')
    
    # Use the most recent activity indicator
    most_recent_age = min(session_age, chat_age)
    
    if most_recent_age < THINKING_THRESHOLD:
        return ("THINKING", "Processing request...")
    elif most_recent_age < WORKING_THRESHOLD:
        return ("WORKING", "Active")
    else:
        return ("IDLE", "Monitoring quietly")


class ActivityMonitor:
    def __init__(self):
        self.running = True
        self.current_state = None
        
    def run(self):
        """Main monitoring loop."""
        print(f"Friday activity monitor starting...")
        print(f"  Session file: {SESSIONS_FILE}")
        print(f"  Log dir: {LOG_DIR}")
        print(f"  State file: {STATE_FILE}")
        print()
        
        # Initial state
        update_state("IDLE", "Monitoring quietly")
        self.current_state = "IDLE"
        
        while self.running:
            try:
                state, description = determine_state()
                
                if state != self.current_state:
                    update_state(state, description)
                    self.current_state = state
                    
                time.sleep(POLL_INTERVAL)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                time.sleep(5)
                
    def stop(self):
        self.running = False


def main():
    monitor = ActivityMonitor()
    
    def signal_handler(signum, frame):
        print("\nShutting down...")
        monitor.stop()
        update_state("IDLE", "Monitor stopped")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    monitor.run()


if __name__ == "__main__":
    main()

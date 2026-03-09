#!/usr/bin/env python3
"""Simple script to update Friday's activity state for the dashboard.

Usage:
    python3 set-friday-state.py IDLE "Monitoring quietly"
    python3 set-friday-state.py THINKING "Processing your question"
    python3 set-friday-state.py WORKING "Running commands"
    python3 set-friday-state.py ALERT "Something needs attention"
"""

import json
import sys
import time
from pathlib import Path

STATE_FILE = Path.home() / ".friday-activity-state"

def update_state(state, description):
    """Update Friday's activity state."""
    data = {
        "state": state.upper(),
        "description": description,
        "timestamp": time.time()
    }
    
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f)
        print(f"✅ Friday state updated: {state} - {description}")
    except IOError as e:
        print(f"❌ Error updating state: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 set-friday-state.py STATE DESCRIPTION")
        print("Valid states: IDLE, THINKING, WORKING, CODING, ALERT, SPEAKING")
        sys.exit(1)
    
    state = sys.argv[1]
    description = sys.argv[2]
    
    valid_states = ["IDLE", "THINKING", "WORKING", "CODING", "ALERT", "SPEAKING"]
    if state.upper() not in valid_states:
        print(f"Invalid state: {state}")
        print(f"Valid states: {', '.join(valid_states)}")
        sys.exit(1)
    
    update_state(state, description)

if __name__ == "__main__":
    main()
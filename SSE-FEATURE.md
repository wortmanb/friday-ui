# Friday UI SSE Activity Stream

## What's New

The dashboard now shows **Friday's real activity state** via Server-Sent Events (SSE) instead of just static system metrics.

## Features

### Real-Time Activity Display
- **Prominent activity section** at the top of the dashboard
- **Live state updates** via SSE (no polling delays)  
- **Animated indicators** that change based on activity
- **Six activity states**: IDLE, THINKING, WORKING, CODING, ALERT, SPEAKING

### State Updates
Friday can update her state in real-time using:
```bash
python3 set-friday-state.py THINKING "Processing your question"
python3 set-friday-state.py WORKING "Running commands"
python3 set-friday-state.py ALERT "Something needs attention"
```

### SSE Endpoint
- **URL**: `http://127.0.0.1:8765/api/activity`
- **Format**: Server-Sent Events with JSON payloads
- **Auto-reconnect**: Dashboard automatically reconnects on connection loss
- **Heartbeat**: 30-second keepalive to maintain connections

## Testing

1. **Start the server**:
   ```bash
   cd ~/git/friday-ui/prototype
   python3 server.py
   ```

2. **Open the dashboard**: `http://127.0.0.1:8765/`

3. **Test state changes**:
   ```bash
   cd ~/git/friday-ui
   python3 set-friday-state.py THINKING "Testing SSE updates"
   python3 set-friday-state.py WORKING "Running background tasks" 
   python3 set-friday-state.py IDLE "Back to monitoring"
   ```

4. **Watch the dashboard** update in real-time as you change states

## Integration

Friday agents can call `set-friday-state.py` to reflect their current activity:
- When starting to think about a problem: `THINKING`
- When executing commands/tools: `WORKING` 
- When writing code: `CODING`
- When speaking (TTS): `SPEAKING`
- When something needs attention: `ALERT`
- When idle: `IDLE`

This gives users immediate visual feedback about what Friday is doing instead of a static dashboard that never changes.
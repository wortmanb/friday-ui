# Friday UI v2 Development

## Vision
Replace the unreliable cat avatar with a useful D3-based visualization dashboard.

## Requirements (from Bret's feedback)
- **Minimal screen footprint** - no screen hogging
- **High reliability** - no connection issues or crashes  
- **Useful data** - visualize information that actually matters
- **Real-time updates** - but robust, not flaky

## D3 Dashboard Ideas
1. **Minimal status widget** - Small corner indicator  
2. **Homelab metrics** - ES health, k8s pods, system resources (selected for prototype)
3. **Interactive service map** - Network topology with health status
4. **Git activity timeline** - Repository activity visualization
5. **Calendar integration** - Meeting timeline with alerts

## Development Plan
- [x] Prototype homelab metrics widget
- [x] Define useful data sources (CPU, memory, disk, load, service checks)
- [x] Design responsive layout
- [x] Implement real-time updates (polling with offline state)
- [ ] User testing with Bret

## Technical Stack
- D3.js for visualization
- WebSocket or SSE for real-time (with fallback)
- Responsive design (mobile-friendly)
- Zero external dependencies where possible

# Friday UI Dashboard

## Version History

**v1.x** (Deprecated) - Cat avatar with particle effects
- Abandoned due to reliability issues and excessive screen usage
- Various feature attempts scattered across multiple repos (anti-pattern)

**v2.x** (In Development) - D3-based visualization dashboard
- Minimal screen footprint
- Reliable real-time updates  
- Useful data visualization focus

## v2 Prototype (D3 Dashboard)

The v2 prototype replaces the v1 cat avatar with a small, D3-powered dashboard that shows real metrics instead of decorative animation.

**Why it’s better than the cat avatar**
- Uses real data (CPU, memory, disk, load, optional service checks)
- Compact corner widget instead of a screen-hogging avatar
- Polling-based updates with a clear offline state

**Try it**
```bash
python3 prototype/server.py
```

Then open:
- `http://127.0.0.1:8765/` for live metrics
- `http://127.0.0.1:8765/demo.html` for demo mode

## Development

Features are developed as branches, not separate repositories.

```bash
git checkout -b feature/your-feature-name
# develop
git push origin feature/your-feature-name
# create PR for review
```

## Branches

- `main` - Current stable release
- `v1-archive` - Original cat avatar implementation (archived)
- `v2-dev` - D3 rewrite development
- `feature/*` - Feature development branches

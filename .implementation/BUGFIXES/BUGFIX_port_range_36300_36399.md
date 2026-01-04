# BUGFIX: Standardize Ports to 36300–36399

**Status:** 🟢 Complete
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Problem
Previous default ports risk conflicts with other local services and system-assigned ports.

## Fix
All runtime ports used by this repo are standardized to the **reserved local range `36300–36399`**.

### Allocations
- **Frontend:** `36300`
- **Backend API:** `36301`

## Files Changed
- docker-compose.yml (host and container ports moved to 36300/36301)
- backend/Dockerfile (EXPOSE/PORT/CMD moved to 36301)
- frontend/server.js (default PORT moved to 36300)
- README.md (endpoints updated)

## Verification
- Rebuild/restart: `make run`
- Frontend: http://localhost:36300
- Backend health: http://localhost:36301/api/health

# Project Team Distribution & Responsibilities

This document defines how the Rate Limiter project can be efficiently divided among a four-person development team to ensure parallel progression and ownership.

## Team Member 1: Core Service & Infrastructure Engineer
**Focus: Redis, Algorithmic Core, and Infrastructure**
- **Responsibilities:**
  - Build and maintain the core `RateLimiter` logic (`rate_limiter/core.py`).
  - Optimize the atomic Lua scripts handling the sliding window logic (`rate_limiter/lua_scripts.py`).
  - Manage Redis integrations (`rate_limiter/redis_client.py`), handling cluster mode, connection pooling, and error fallbacks.
  - Maintain infrastructure and deployment setups (Docker, `docker-compose.yml`, `DEPLOYMENT.md`).

## Team Member 2: Integrations & Backend Engineer
**Focus: Adapters, Framework Implementations, and Test Backend**
- **Responsibilities:**
  - Develop and maintain all framework adapters (`rate_limiter/adapters/` for FastAPI, Flask, Django).
  - Manage the `test_backend/main.py` application serving the API and AI analysis endpoints.
  - Ensure headers (e.g., `ratelimit-remaining`, `retry-after`) conform exactly to rate limiting RFC standards.
  - Work on hot-swappable configuration APIs (`/api/config`).

## Team Member 3: Frontend & Data Visualization Engineer
**Focus: Dashboard, UI/UX, and Live Metrics Tracking**
- **Responsibilities:**
  - Build and maintain the React dashboard interface (`test_frontend/src/App.jsx`).
  - Integrate live metrics polling and implement the Recharts-based real-time request analytics visualization.
  - Handle state management and interactive features (e.g., "Burst Requests", customizing keys).
  - Polish styling, UI feedback, and error reporting components within `index.css`.

## Team Member 4: Quality Assurance, Security & Tech Lead
**Focus: Testing, Stability, Documentation, and AI Integration**
- **Responsibilities:**
  - Overlook project quality, security edge-cases, and testing coverage (`test_backend/test_rate_limits.py`).
  - Maintain project documentation (`API_REFERENCE.md`, `USAGE_GUIDE.md`, this document).
  - Develop and configure the Gemini AI Insights generation workflow representing the security consultant evaluation layer.
  - Handle code-reviews, coordinate merging, and verify `fail_open` and `skip_rules` behaviors.

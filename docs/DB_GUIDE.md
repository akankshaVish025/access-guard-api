# Database Guide (FastAPI + SQLAlchemy + SQLite)

## 1) Configuration
- Source of truth is `DATABASE_URL` in environment; fallback is `sqlite:///./app.db`.
- Current setup is in `app/core/config.py` and `app/db/session.py`.
- Rule: keep secrets and connection strings out of source code.

## 2) Engine and Session Lifecycle
- `engine` is process-wide and reused.
- `SessionLocal` is request-scoped through `get_db()`.
- `get_db()` behavior:
  - Yields session to endpoint/service.
  - `commit()` on success.
  - `rollback()` on failure.
  - Always `close()`.
- Why this matters:
  - Prevents leaked connections.
  - Keeps transactions atomic.

## 3) SQLite Production-Safety PRAGMAs
- Enabled in `app/db/session.py`:
  - `foreign_keys=ON`: enforce relational integrity.
  - `journal_mode=WAL`: better write/read concurrency.
  - `synchronous=NORMAL`: good durability/performance balance.
- Note: SQLite is good for small/medium apps or single-node deployments.

## 4) Schema Design Rules Used
- `users.email` is `UNIQUE + INDEX`.
- `data_access.email_id` references `users.email` with cascade delete.
- `data_access.auth_token` is `UNIQUE + INDEX`.
- Access telemetry fields:
  - `counter`
  - `last_access`
- OTP fields:
  - `otp_code`
  - `otp_expires_at`

## 5) Query Safety and Performance
- Protected read endpoint validates token before query.
- `field_name` is allow-listed (prevents accidental broad exposure).
- Pagination (`limit`, `offset`) protects from unbounded reads.
- Prefix filter (`name_prefix`) demonstrates safe extensible filtering.

## 6) Transaction Strategy
- Business logic executes inside one DB transaction per request.
- Service layer performs operations; dependency handles commit/rollback.
- Pattern to follow:
  - Validate input
  - Load entities
  - Apply state changes
  - Flush/refresh if needed
  - Return stable response

## 7) Operational Monitoring (Minimum)
- Watch:
  - Request error rate (5xx)
  - DB lock contention and slow queries
  - Token validation failures (possible abuse)
  - OTP failure/expiry rates
- Keep structured logs around auth and DB failures.

## 8) Migration Strategy (Next Upgrade)
- Current app uses `Base.metadata.create_all()` for bootstrap.
- For production change management, move to Alembic:
  - Create revision for every schema change.
  - Review SQL before deployment.
  - Run migrations in CI/CD before app rollout.
- Never change production schema manually if migration history exists.

## 9) Common Mistakes to Avoid
- Sharing one global session across requests.
- Returning all rows without pagination.
- Storing OTP in logs or API responses in production.
- Not indexing lookup columns (`email`, `auth_token`).
- Skipping rollback paths on exceptions.

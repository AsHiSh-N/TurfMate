# TurfMate

TurfMate is a sports venue marketplace for discovering courts, checking availability, and booking sports facilities.

## Quick start

### Docker Compose

```bash
docker compose up --build
```

Open http://localhost:3000. The API docs are at http://localhost:8000/docs.
The backend uses a persistent SQLite volume and seeds demo users and an active venue on startup.

Stop the stack with `docker compose down`.

### Manual development

Use two terminals from the repository root. In terminal one:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.seed
uvicorn app.main:app --reload
```

In terminal two:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. The default backend database is SQLite, so a separate PostgreSQL installation is not required for local development.

### Browser E2E

With the backend virtual environment and frontend dependencies installed, run:

```bash
cd frontend
npm run e2e
```

The Playwright suite starts isolated backend/frontend services and seeds a temporary SQLite database; it does not use the local application database.

## Application routes

- `/` customer venue discovery and booking
- `/login` authentication
- `/bookings` customer booking history and cancellation
- `/owner` venue owner studio
- `/admin` admin approval and operations console

## Documentation

See [docs/RELEASE_GUIDE.md](docs/RELEASE_GUIDE.md) for:

- Complete functionality inventory
- Role permissions
- API route inventory
- Customer, owner, and admin workflows
- Local and Docker setup
- Verification status
- Production launch limitations and checklist

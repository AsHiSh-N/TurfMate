from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.routes import router as auth_router
from app.api.venues.routes import router as venue_router
from app.api.bookings.routes import router as booking_router
from app.api.owner.routes import router as owner_router
from app.api.admin.routes import router as admin_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app import models

settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title='TurfMate API', version='1.0.0')
allowed_origins = [settings.FRONTEND_URL]
if settings.FRONTEND_URL in {'http://localhost:3000', 'http://127.0.0.1:3000'}:
    allowed_origins = [
        'http://localhost:3000', 'http://127.0.0.1:3000',
        'http://localhost:3001', 'http://127.0.0.1:3001',
    ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(auth_router, prefix='/api/auth')
app.include_router(venue_router, prefix='/api')
app.include_router(booking_router, prefix='/api')
app.include_router(owner_router, prefix='/api/owner')
app.include_router(admin_router, prefix='/api/admin')


@app.get('/health')
def health():
    return {'status': 'ok'}

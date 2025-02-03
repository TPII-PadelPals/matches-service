from fastapi import APIRouter

from app.api.routes import items, items_service, matches_players, provisional_matches

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(
    provisional_matches.router,
    prefix="/provisional-matches",
    tags=["provisional-matches"],
)
api_router.include_router(
    matches_players.router,
    prefix="/provisional-matches/{match_public_id}/players",
    tags=["matches-players"],
)
api_router.include_router(
    items_service.router, prefix="/items-service", tags=["items-service"]
)

from fastapi import APIRouter

from app.api.routes import (
    items,
    items_service,
    matches,
    matches_players,
    players_matches,
)

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(
    items_service.router, prefix="/items-service", tags=["items-service"]
)
api_router.include_router(
    matches.router,
    prefix="/matches",
    tags=["matches"],
)
api_router.include_router(
    matches_players.router,
    prefix="/matches/{match_public_id}/players",
    tags=["matches-players"],
)
api_router.include_router(
    players_matches.router,
    prefix="/players/{user_public_id}/matches",
    tags=["players"],
)

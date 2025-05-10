from app.core.config import settings
from app.models.match_extended import MatchExtended
from app.models.payment import Payment

from .base_service import BaseService


class PaymentsService(BaseService):
    def __init__(self) -> None:
        """Init the service."""
        super().__init__()
        self._set_base_url(
            is_http=True,
            host=settings.PAYMENTS_SERVICE_HOST,
            port=settings.PAYMENTS_SERVICE_PORT,
        )
        if settings.PAYMENTS_SERVICE_API_KEY:
            self.set_base_headers({"x-api-key": settings.PAYMENTS_SERVICE_API_KEY})

    async def create_payment(self, match_player_extended: MatchExtended) -> Payment:
        match_player_extended_public = match_player_extended.to_public()

        content = await self.post(
            "/api/v1/payments", json=match_player_extended_public.model_dump_json()
        )

        payment = Payment(
            public_id=content["public_id"],
            match_public_id=content["match_public_id"],
            user_public_id=content["user_public_id"],
            pay_url=content["pay_url"],
        )

        return payment

import uuid
from datetime import datetime
from typing import Any

from app.models.match import Match
from app.models.match_player import MatchPlayer, ReserveStatus


class MatchMorningPaseoColon:
    match_public_id = "0f565d41-e596-48f2-bbe4-74035c44ce18"
    court_morning_uuid = "32b5b0a8-3813-4dcc-aba9-34d1f046a93c"
    court_morning_name = "Cancha Mañana"
    time = 9
    date = datetime.strptime("1/5/2025", "%d/%m/%Y").date()
    assigned_id = "db08d286-58cf-4542-8501-efa273e38be4"

    @classmethod
    def records(cls) -> list[Any]:
        return cls.match() + cls.match_players()

    @classmethod
    def match(cls) -> list[Any]:
        matches = [
            Match(
                public_id=cls.match_public_id,
                court_name=cls.court_morning_name,
                court_public_id=cls.court_morning_uuid,
                time=cls.time,
                date=cls.date,
            )
        ]
        return matches

    @classmethod
    def match_players(cls) -> list[Any]:
        match_players = []
        match_players.append(
            MatchPlayer(
                match_public_id=cls.match_public_id,
                user_public_id=cls.assigned_id,
                distance=0,
                reserve=ReserveStatus.ASSIGNED,
            )
        )
        for _ in range(3):
            match_players.append(
                MatchPlayer(
                    match_public_id=cls.match_public_id,
                    user_public_id=uuid.uuid4(),
                    distance=0,
                    reserve=ReserveStatus.SIMILAR,
                )
            )
        return match_players


RECORDS: list[Any] = []
RECORDS += MatchMorningPaseoColon.records()

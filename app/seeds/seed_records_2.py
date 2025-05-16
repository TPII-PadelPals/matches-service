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
    assigned_uuid = "db08d286-58cf-4542-8501-efa273e38be4"
    similar_uuids = [
        "3cbccfa2-65d7-4d49-b801-b7f30daae857",
        "96ff36d6-bd6e-49c3-a666-cda2d2865be0",
        "a80a64fb-9672-450c-a98e-bcf366ea6ac8",
    ]

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
                user_public_id=cls.assigned_uuid,
                distance=0,
                reserve=ReserveStatus.ASSIGNED,
            )
        )
        for similar_uuid in cls.similar_uuids:
            match_players.append(
                MatchPlayer(
                    match_public_id=cls.match_public_id,
                    user_public_id=similar_uuid,
                    distance=0,
                    reserve=ReserveStatus.SIMILAR,
                )
            )
        return match_players


RECORDS: list[Any] = []
RECORDS += MatchMorningPaseoColon.records()

import random
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.models.match import Match
from app.models.match_player import MatchPlayer, ReserveStatus

MATCH_UUID = "0f565d41-e596-48f2-bbe4-74035c44ce18"
COURT_UUID = "3" "2b5b0a8-3813-4dcc-aba9-34d1f046a93c"
COURT_NAME = "C001"
TIME = 9
DATE = datetime.strptime("1/5/2025", "%d/%m/%Y").date()
ASSIGNED_UUID = "db08d286-58cf-4542-8501-efa273e38be4"
SIMILAR_UUIDS = [
    "3cbccfa2-65d7-4d49-b801-b7f30daae857",
    # "96ff36d6-bd6e-49c3-a666-cda2d2865be0",
    # "a80a64fb-9672-450c-a98e-bcf366ea6ac8",
]


class MatchSeed:
    def __init__(
        self,
        match_uuid: str,
        court_uuid: str,
        court_name: str,
        date: str,
        time: int,
        assigned_uuid: str,
        similar_uuids: list[str],
        status: str,
    ) -> None:
        self.match = Match(
            public_id=match_uuid,
            court_public_id=court_uuid,
            court_name=court_name,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            time=time,
            status=status,
        )
        self.match_players = []
        self.match_players.append(
            MatchPlayer(
                match_public_id=match_uuid,
                user_public_id=assigned_uuid,
                distance=0,
                reserve=ReserveStatus.INSIDE,
            )
        )
        for similar_uuid in similar_uuids:
            self.match_players.append(
                MatchPlayer(
                    match_public_id=match_uuid,
                    user_public_id=similar_uuid,
                    distance=0,
                    reserve=ReserveStatus.INSIDE,
                )
            )

    def records(self) -> list[Any]:
        return [self.match] + self.match_players


RECORDS: list[Any] = []
COURT_PUBLIC_ID = "b7e5b8d6-aeed-4537-88b7-f41b6d4ac53a"
for day in range(8, 15):
    for i in range(9, 24):
        if random.random() > 0.5:
            RECORDS += MatchSeed(
                str(uuid4()),
                COURT_PUBLIC_ID,
                "C001",
                f"2025-06-{day:02d}",
                i,
                ASSIGNED_UUID,
                SIMILAR_UUIDS,
                random.choice(["Provisional", "Reserved"]),
            ).records()

from app.core.config import Settings


def set_provisional_match_data(player_id_1, player_id_2, court_id, time, date):
    return {
        "player_id_1": player_id_1,
        "player_id_2": player_id_2,
        "court_id": court_id,
        "time": time,
        "date": date,
    }


async def create_provisional_match(async_client, x_api_key_header, data):
    return await async_client.post(
        f"{Settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        json=data,
    )
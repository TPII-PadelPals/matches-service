from fastapi import status

# Common responses
NOT_ENOUGH_PERMISSIONS = {
    status.HTTP_403_FORBIDDEN: {"description": "Not enough permissions"}
}

# Item responses
ITEM_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Item not found"}}
ITEM_RESPONSES = {**ITEM_NOT_FOUND, **NOT_ENOUGH_PERMISSIONS}

PATCH_MATCHES_PLAYERS = {
    status.HTTP_200_OK: {
        "description": "Updated match player",
        "content": {"application/json": {"examples": {"reserve": "inside"}}},
    },
    status.HTTP_401_UNAUTHORIZED: {"description": "This change is not authorized"},
}

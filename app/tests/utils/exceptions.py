from fastapi import HTTPException, status

class NotUniqueException(HTTPException):
    def __init__(self, item: str) -> None:
        detail = f"{item.capitalize()} already exists."
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
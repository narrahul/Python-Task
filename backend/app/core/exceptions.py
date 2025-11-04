from http import HTTPStatus


class APIError(Exception):
    def __init__(self, message: str, *, status_code: int = HTTPStatus.BAD_REQUEST, extra: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}

    def to_dict(self) -> dict:
        payload = {"message": self.message}
        if self.extra:
            payload["details"] = self.extra
        return payload

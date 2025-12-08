import os

API_TOKEN = os.getenv('FALLAT_API_TOKEN')


def verify_token(token: str | None) -> bool:
    if API_TOKEN is None:
        return True
    return token == API_TOKEN

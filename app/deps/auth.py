from functools import lru_cache
from collections.abc import Callable

from fastapi import Cookie, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.models.users import UserProfile
from app.services.users import SESSION_COOKIE_NAME, SQLiteUserStore


@lru_cache
def _get_cached_user_store(db_path: str) -> SQLiteUserStore:
    store = SQLiteUserStore(db_path)
    store.initialize()
    return store


def get_user_store(settings: Settings = Depends(get_settings)) -> SQLiteUserStore:
    if settings.room_store_backend != "sqlite":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="User accounts currently require the SQLite room backend.",
        )
    return _get_cached_user_store(settings.room_store_path)


def _resolve_user(
    required: bool,
) -> Callable[[str | None, SQLiteUserStore], UserProfile | None]:
    def dependency(
        session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
        user_store: SQLiteUserStore = Depends(get_user_store),
    ) -> UserProfile | None:
        user = user_store.get_user_by_session(session_token)
        if required and user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login required.",
            )
        return user

    return dependency


get_current_user = _resolve_user(required=True)
get_optional_current_user = _resolve_user(required=False)

from __future__ import annotations

import json
import logging
from urllib.parse import urlencode

from app.config import Settings
from app.models.users import UserNotification
from app.services.users import SQLiteUserStore

try:
    from pywebpush import WebPushException, webpush
except ImportError:  # pragma: no cover - dependency may be unavailable in some dev environments
    WebPushException = Exception  # type: ignore[assignment]
    webpush = None


logger = logging.getLogger(__name__)


def web_push_is_configured(settings: Settings) -> bool:
    return bool(
        webpush
        and settings.web_push_public_key
        and settings.web_push_private_key
        and settings.web_push_subject
    )


def notification_target_url(notification: UserNotification) -> str:
    query: dict[str, str] = {}
    if notification.room_id:
        query["room"] = notification.room_id
    invite_code = str(notification.metadata.get("invite_code", "")).strip()
    if invite_code:
        query["invite"] = invite_code
    if not query:
        return "/"
    return f"/?{urlencode(query)}"


def notification_push_payload(notification: UserNotification) -> dict[str, object]:
    return {
        "title": notification.title,
        "body": notification.body,
        "tag": f"bunny-{notification.notification_type}-{notification.room_id or notification.notification_id}",
        "url": notification_target_url(notification),
        "icon": "/static/bunny-transparent.png?v=20260323-ui-service-147",
        "badge": "/static/bunny-transparent.png?v=20260323-ui-service-147",
        "data": {
            "notification_id": notification.notification_id,
            "room_id": notification.room_id,
            "notification_type": notification.notification_type,
            "url": notification_target_url(notification),
        },
    }


def send_web_push_notification(
    settings: Settings,
    user_store: SQLiteUserStore,
    user_id: str,
    notification: UserNotification,
) -> int:
    if not web_push_is_configured(settings):
        return 0
    if not user_store.user_notifications_enabled(user_id):
        return 0
    subscriptions = user_store.list_push_subscriptions(user_id)
    if not subscriptions:
        return 0

    delivered = 0
    payload = json.dumps(notification_push_payload(notification), ensure_ascii=False)
    vapid_claims = {"sub": settings.web_push_subject}

    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription.model_dump(mode="json"),
                data=payload,
                vapid_private_key=settings.web_push_private_key,
                vapid_claims=vapid_claims,
            )
            delivered += 1
        except WebPushException as exc:  # pragma: no cover - network/runtime dependent
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code in {404, 410}:
                user_store.delete_push_subscription(user_id, subscription.endpoint)
                continue
            logger.warning("Web push delivery failed for %s: %s", user_id, exc)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Unexpected web push failure for %s: %s", user_id, exc)
    return delivered

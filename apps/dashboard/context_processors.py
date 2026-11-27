"""Exposes the current user's unread notifications to every template."""

from __future__ import annotations


def notifications(request):
    if not request.user.is_authenticated:
        return {"unread_notifications": [], "unread_notification_count": 0}

    queryset = request.user.notifications.filter(is_read=False)[:5]
    return {
        "unread_notifications": queryset,
        "unread_notification_count": request.user.notifications.filter(
            is_read=False
        ).count(),
    }

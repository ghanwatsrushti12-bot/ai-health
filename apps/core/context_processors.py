"""Global template context available on every page."""

from django.conf import settings


def site_meta(request):
    """Expose site-wide branding constants to all templates."""
    return {
        "SITE_NAME": "CarePulse",
        "SITE_TAGLINE": "Smart care, seamlessly coordinated.",
        "SUPPORT_PHONE": "+91 1800-200-3000",
        "SUPPORT_EMAIL": "support@carepulse.local",
        "DEBUG": settings.DEBUG,
    }

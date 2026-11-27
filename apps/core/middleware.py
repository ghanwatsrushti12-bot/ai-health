"""Lightweight custom middleware for CarePulse."""

import logging

logger = logging.getLogger("carepulse")


class RequestExceptionLoggingMiddleware:
    """Logs unhandled exceptions with the request path for easier debugging.

    Django already logs 500s, but this keeps a project-specific, structured
    trail in ``logs/carepulse.log`` distinct from the noisier ``django``
    logger, which is useful once several apps are involved.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.path,
            exception,
            exc_info=True,
        )
        return None

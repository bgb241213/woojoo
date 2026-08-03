"""Keeps the retention purge running without a scheduler.

Railway runs this site as a single web service with no cron, so a purge wired
only into the deploy command would stop happening the moment deploys stop.
This triggers it from ordinary traffic instead, at most once a day.

Failures are logged and swallowed on purpose — a problem expiring old data must
never take the public site down.
"""
import logging

from django.core.cache import cache

from . import retention

logger = logging.getLogger(__name__)

PURGE_INTERVAL_SECONDS = 60 * 60 * 24
_LOCK_KEY = 'quotes:retention-purge-ran'


class RetentionPurgeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._purge_once_a_day()
        return response

    def _purge_once_a_day(self):
        if cache.get(_LOCK_KEY):
            return
        # Claim the slot before doing the work so concurrent requests don't all
        # start purging at the same moment.
        cache.set(_LOCK_KEY, True, PURGE_INTERVAL_SECONDS)
        try:
            counts = retention.purge()
        except Exception:
            logger.exception('Retention purge failed')
            return
        if counts['quotes'] or counts['callbacks']:
            logger.info(
                'Retention purge removed %s quote(s) and %s callback(s).',
                counts['quotes'], counts['callbacks'],
            )

"""How long submitted personal data may be kept, and the deletion that enforces it.

개인정보보호법 제21조 requires personal data to be destroyed without delay once
its retention period lapses — a policy that promises deletion but never deletes
is worse than no policy at all.

The privacy policy page, the consent notices on the forms, and the purge command
all read these same numbers so the published promise and the actual behaviour
cannot drift apart. Changing a period here changes it everywhere.
"""
from datetime import timedelta

from django.utils import timezone

# Retention periods, in years, measured from the date the enquiry was submitted.
QUOTE_RETENTION_YEARS = 3
CALLBACK_RETENTION_YEARS = 1


def cutoff(years):
    """Records created before this instant are past their retention period."""
    return timezone.now() - timedelta(days=round(years * 365.25))


def expired_quotes():
    from .models import QuoteRequest
    return QuoteRequest.objects.filter(created_at__lt=cutoff(QUOTE_RETENTION_YEARS))


def expired_callbacks():
    from .models import CallbackRequest
    return CallbackRequest.objects.filter(created_at__lt=cutoff(CALLBACK_RETENTION_YEARS))


def purge():
    """Hard-delete every record past its retention period.

    Deletion must be irreversible to count as 파기 — flagging rows as hidden
    would not satisfy the law. Related QuoteItem rows cascade automatically.

    Returns {'quotes': n, 'callbacks': n}.
    """
    quotes = expired_quotes()
    callbacks = expired_callbacks()
    counts = {'quotes': quotes.count(), 'callbacks': callbacks.count()}
    if counts['quotes']:
        quotes.delete()
    if counts['callbacks']:
        callbacks.delete()
    return counts

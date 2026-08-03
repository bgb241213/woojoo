"""Retention periods for templates.

The callback consent notice lives in base.html, which every view renders, so the
numbers reach it through a context processor rather than being retyped there.
"""
from . import retention


def retention_periods(request):
    return {
        'quote_retention_years': retention.QUOTE_RETENTION_YEARS,
        'callback_retention_years': retention.CALLBACK_RETENTION_YEARS,
    }

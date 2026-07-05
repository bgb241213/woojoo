"""Import sales records from data/records.json (Claude Design dataset).

Photos are served from the committed static library at
``static/images/records/<id>/``; each record stores that folder id as
``photo_key`` so the wall can render them without per-image DB rows.
"""
import datetime
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from records.models import SalesRecord


class Command(BaseCommand):
    help = 'Import/sync sales records from data/records.json (Claude Design dataset).'

    @transaction.atomic
    def handle(self, *args, **options):
        source = settings.BASE_DIR / 'data' / 'records.json'
        items = json.loads(source.read_text(encoding='utf-8'))['records']

        created = updated = 0
        for it in items:
            defaults = {
                'model_name': it.get('model', '') or '',
                'shipped_date': datetime.date.fromisoformat(it['date']),
                'is_active': True,
            }
            _, was_created = SalesRecord.objects.update_or_create(
                photo_key=it['id'], defaults=defaults,
            )
            created += was_created
            updated += not was_created

        self.stdout.write(self.style.SUCCESS(
            f'Sales records sync complete: {created} created, {updated} updated. '
            f'Total active: {SalesRecord.objects.filter(is_active=True).count()}'
        ))

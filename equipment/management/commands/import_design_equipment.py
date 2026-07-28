"""Sync the Equipment table to the Claude Design dataset (data/equipment.json).

The design's photo folders are keyed by equipment id, so this command upserts
each item by explicit pk to keep ids aligned. Equipment not present in the
design file is deactivated (not deleted) to preserve historical data.
"""
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from equipment.models import Equipment

CATEGORY_MAP = {
    '5M급': '5m', '6M급': '6m', '7M급': '7m', '8M급': '8m',
    '10M급': '10m', '12M급': '12m', '14M급': '14m', '기타장비': 'etc',
}
TYPE_MAP = {'시저': 'scissor', '굴절': 'boom', '버티칼': 'vertical', '기타': 'other'}


class Command(BaseCommand):
    help = 'Import/sync equipment from data/equipment.json (Claude Design dataset).'

    @transaction.atomic
    def handle(self, *args, **options):
        source = settings.BASE_DIR / 'data' / 'equipment.json'
        items = json.loads(source.read_text(encoding='utf-8'))['equipment']

        seen_ids = []
        created = updated = 0
        for it in items:
            specs = it['specs']
            defaults = {
                'name': it['name'],
                'category': CATEGORY_MAP[it['category']],
                'type': TYPE_MAP[it['type']],
                'description': it.get('description', ''),
                'is_for_sale': it.get('is_for_sale', False),
                'is_for_rent': it.get('is_for_rent', True),
                'is_flagship': it.get('is_flagship', False),
                'is_active': it.get('is_active', True),
                'max_work_height': specs['작업가능높이'],
                'max_platform_height': specs['발판최대높이'],
                'equipment_weight': specs['장비무게'],
                'max_load': specs['적재가능중량'],
                'equipment_size': specs['장비크기'],
                'platform_size': specs['작업대크기'],
                'power_type': specs['동력'],
            }
            obj, was_created = Equipment.objects.update_or_create(pk=it['id'], defaults=defaults)
            seen_ids.append(obj.pk)
            created += was_created
            updated += not was_created

        # Deactivate equipment that is no longer part of the design catalog.
        deactivated = (
            Equipment.objects.filter(is_active=True)
            .exclude(pk__in=seen_ids)
            .update(is_active=False)
        )

        self.stdout.write(self.style.SUCCESS(
            f'Equipment sync complete: {created} created, {updated} updated, '
            f'{deactivated} deactivated. Total active: {Equipment.objects.filter(is_active=True).count()}'
        ))

"""Seed the 16M-class Dingli JCPT1612AC.

Same reasoning as 0011: ``ensure_fixtures`` skips a non-empty database, so the
live site only picks up a new machine if ``migrate`` creates it.
"""
from django.db import migrations

EQUIPMENT_ID = 34

FIELDS = {
    'name': 'JCPT1612AC',
    'category': '16m',
    'type': 'scissor',
    'description': (
        '16M급 전동 시저형 고소작업대. 작업가능높이 15.7m로 고층 실내 작업에 대응하며, '
        '확장 발판을 포함한 작업대(2.64 x 1.12m)에 250kg까지 적재할 수 있습니다.'
    ),
    'max_work_height': '15.7m',
    'max_platform_height': '13.7m',
    'equipment_weight': '3,360kg',
    'max_load': '250kg',
    'equipment_size': '2.84 x 1.25 x 2.62m',
    'platform_size': '2.64 x 1.12m',
    'power_type': '배터리',
    'is_active': True,
    'is_for_rent': True,
    'is_for_sale': False,
    'is_flagship': False,
}


def add_equipment(apps, schema_editor):
    Equipment = apps.get_model('equipment', 'Equipment')
    Equipment.objects.get_or_create(pk=EQUIPMENT_ID, defaults=FIELDS)


def remove_equipment(apps, schema_editor):
    Equipment = apps.get_model('equipment', 'Equipment')
    Equipment.objects.filter(pk=EQUIPMENT_ID, name=FIELDS['name']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0011_seed_lgmg_as1413e'),
    ]

    operations = [
        migrations.RunPython(add_equipment, remove_equipment),
    ]

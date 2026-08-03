"""Seed the 16M-class LGMG AS1413E.

``ensure_fixtures`` only loads the fixture into an empty database, so on the
live site (which already has rows) a new machine would never appear. Adding it
here means ``migrate`` — the first step of the deploy — creates it exactly once.
``import_design_photos`` runs later in the same boot and uploads
``static/images/rental/33/*.png`` against this id.
"""
from django.db import migrations

EQUIPMENT_ID = 33

FIELDS = {
    'name': 'LGMG AS1413E',
    'category': '16m',
    'type': 'scissor',
    'description': (
        '16M급 전동 시저형 고소작업대. 작업가능높이 15.8m로 고층 실내 작업에 대응하며, '
        '확장 발판을 포함한 작업대(2.64 x 1.12m)에 320kg까지 적재할 수 있습니다.'
    ),
    'max_work_height': '15.8m',
    'max_platform_height': '13.8m',
    'equipment_weight': '3,570kg',
    'max_load': '320kg',
    'equipment_size': '2.8 x 1.3 x 2.74m',
    'platform_size': '2.64 x 1.12m',
    'power_type': '배터리',
    'is_active': True,
    'is_for_rent': True,
    'is_for_sale': False,
    'is_flagship': False,
}


def add_equipment(apps, schema_editor):
    Equipment = apps.get_model('equipment', 'Equipment')
    # get_or_create, not update_or_create: if staff have already added or edited
    # this machine in the admin, their version wins.
    Equipment.objects.get_or_create(pk=EQUIPMENT_ID, defaults=FIELDS)


def remove_equipment(apps, schema_editor):
    Equipment = apps.get_model('equipment', 'Equipment')
    Equipment.objects.filter(pk=EQUIPMENT_ID, name=FIELDS['name']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0010_alter_equipment_category'),
    ]

    operations = [
        migrations.RunPython(add_equipment, remove_equipment),
    ]

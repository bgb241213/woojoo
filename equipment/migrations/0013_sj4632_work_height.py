"""Correct SJ4632's working height: 11.6m -> 12m.

This machine already exists on the live site, so unlike the 16M seeds it has to
be an UPDATE. Guarded on the old value: if staff have since changed the field in
the admin, their value is left alone.
"""
from django.db import migrations

EQUIPMENT_ID = 22
OLD, NEW = '11.6m', '12m'


def set_new(apps, schema_editor):
    Equipment = apps.get_model('equipment', 'Equipment')
    Equipment.objects.filter(pk=EQUIPMENT_ID, max_work_height=OLD).update(max_work_height=NEW)


def set_old(apps, schema_editor):
    Equipment = apps.get_model('equipment', 'Equipment')
    Equipment.objects.filter(pk=EQUIPMENT_ID, max_work_height=NEW).update(max_work_height=OLD)


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0012_seed_jcpt1612ac'),
    ]

    operations = [
        migrations.RunPython(set_new, set_old),
    ]

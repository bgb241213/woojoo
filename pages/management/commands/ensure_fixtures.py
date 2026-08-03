"""Seed the equipment catalogue into a brand-new database.

Runs on every boot. With Postgres the table survives deploys, so after the first
run this does nothing and staff edits made in the admin are never touched.

The guard is deliberately "no equipment at all" rather than a row count: once
the catalogue is being maintained from the admin, the fixture is a starting
point and not a target to sync back to. Seeding a table that already holds rows
would overwrite whatever staff changed.

History note — this command once silently did nothing on a fresh database
because a data migration had inserted two rows before it ran, so the guard saw a
non-empty table and skipped the other 32 machines. Hence --force, and hence the
rule that catalogue seed data belongs in the fixture, never in a migration.
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand

from equipment.models import Equipment

FIXTURE = 'equipment_data'


class Command(BaseCommand):
    help = '장비 목록이 비어 있으면 초기 데이터를 넣습니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Load the fixture even when equipment already exists. Overwrites '
                 'rows whose pk matches the fixture — admin edits to those rows are lost.',
        )

    def handle(self, *args, **options):
        existing = Equipment.objects.count()

        if existing and not options['force']:
            self.stdout.write(
                f'[ensure_fixtures] 장비 {existing}건이 이미 있어 건너뜁니다. '
                '(초기 데이터를 다시 넣으려면 --force)'
            )
            return

        if existing:
            self.stdout.write(
                self.style.WARNING(f'[ensure_fixtures] --force: 기존 {existing}건 위에 덮어씁니다.')
            )

        call_command('loaddata', FIXTURE, verbosity=0)
        self.stdout.write(self.style.SUCCESS(
            f'[ensure_fixtures] 장비 {Equipment.objects.count()}건을 불러왔습니다.'
        ))

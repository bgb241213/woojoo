from django.core.management.base import BaseCommand
from django.core.management import call_command
from equipment.models import Equipment


class Command(BaseCommand):
    help = 'Load equipment fixtures if DB is empty'

    def handle(self, *args, **options):
        if Equipment.objects.exists():
            self.stdout.write(
                f'[ensure_fixtures] {Equipment.objects.count()} equipment records exist — skipped.'
            )
        else:
            call_command('loaddata', 'equipment_data')
            self.stdout.write(
                self.style.SUCCESS(
                    f'[ensure_fixtures] Loaded {Equipment.objects.count()} equipment records.'
                )
            )

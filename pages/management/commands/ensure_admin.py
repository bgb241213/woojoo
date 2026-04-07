from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create admin superuser if not exists'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = 'admin1234'

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'[ensure_admin] "{username}" already exists — skipped.')
        else:
            User.objects.create_superuser(username=username, email='', password=password)
            self.stdout.write(
                self.style.SUCCESS(f'[ensure_admin] Superuser "{username}" created.')
            )

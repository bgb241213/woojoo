"""Delete enquiries whose retention period has lapsed.

Runs on every deploy (see railway.toml / Procfile) and once a day from the
running site, so the data actually disappears on schedule rather than only
when someone remembers to press a button.

Use --dry-run to see what would go before it goes.
"""
from django.core.management.base import BaseCommand

from quotes import retention


class Command(BaseCommand):
    help = '보유기간이 지난 견적·콜백 신청의 개인정보를 파기합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report what would be deleted without deleting anything.',
        )

    def handle(self, *args, **options):
        quotes = retention.expired_quotes().count()
        callbacks = retention.expired_callbacks().count()

        self.stdout.write(
            f'보유기간 — 견적 {retention.QUOTE_RETENTION_YEARS}년 / '
            f'콜백 {retention.CALLBACK_RETENTION_YEARS}년'
        )

        if options['dry_run']:
            self.stdout.write(
                f'[dry-run] 파기 대상: 견적 {quotes}건, 콜백 {callbacks}건 '
                '(실제로 삭제하지 않았습니다)'
            )
            return

        if not quotes and not callbacks:
            self.stdout.write(self.style.SUCCESS('파기 대상 없음.'))
            return

        counts = retention.purge()
        self.stdout.write(self.style.SUCCESS(
            f'파기 완료 — 견적 {counts["quotes"]}건, 콜백 {counts["callbacks"]}건'
        ))

"""판매 실적 사진을 DB 로 옮긴다 — 배포마다 실행된다.

사진이 ``static/images/records/<폴더 ID>/`` 에 파일로만 있고 DB 에는 없었다.
어드민의 사진 칸은 늘 비어 보였고, 화면과 DB 가 서로 다른 곳을 봤다.

실적 하나가 사진 한 장이므로, 폴더에 사진이 여러 장이면 첫 장은 그 실적이
가져가고 나머지는 같은 정보를 복사한 새 실적이 된다.

멱등이다. 사진이 이미 붙은 실적은 건너뛰므로, 여러 번 돌아도 실적이 불어나지
않는다.
"""
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from equipment.imaging import encode_webp
from equipment.photos import record_photos
from records.models import SalesRecord

# 이 명령이 올리는 파일은 전부 이 아래. 바깥 경로는 어드민 업로드다
# (ImageField upload_to 가 'records/' 라 records/<원본파일명> 으로 떨어진다).
DESIGN_PREFIX = 'records/design/'


def stored_name(record_key, index):
    """옮긴 사진이 저장소에서 갖는 경로. 원본 폴더 구조를 그대로 따른다."""
    return f'{DESIGN_PREFIX}{record_key}/{index}.webp'


class Command(BaseCommand):
    help = '판매 실적 사진을 정적 파일에서 DB 로 옮깁니다.'

    def handle(self, *args, **options):
        uploaded = attached = split = skipped = 0

        for record in SalesRecord.objects.exclude(photo_key=None).order_by('photo_key'):
            if record.image:
                skipped += 1
                continue

            sources = record_photos(record.photo_key)
            if not sources:
                continue

            for index, url in enumerate(sources):
                name = stored_name(record.photo_key, index)
                if not default_storage.exists(name):
                    source = self._source_path(url)
                    if source is None:
                        self.stderr.write(self.style.WARNING(f'  ! 파일 없음: {url}'))
                        continue
                    data, _ = encode_webp(source.read_bytes())
                    default_storage.save(name, ContentFile(data))
                    uploaded += 1

                if index == 0:
                    record.image = name
                    # image 는 이미 저장소에 있는 경로다. save() 의 변환기를
                    # 태우면 이름이 upload_to 를 한 번 더 거쳐 중첩된다.
                    super(SalesRecord, record).save(update_fields=['image'])
                    attached += 1
                else:
                    extra = SalesRecord(
                        image=name,
                        model_name=record.model_name,
                        shipped_date=record.shipped_date,
                        photo_key=None,
                        is_active=record.is_active,
                    )
                    super(SalesRecord, extra).save()
                    split += 1

        self.stdout.write(self.style.SUCCESS(
            f'판매 실적 사진: {attached}건에 사진 연결, {split}건 새로 생성, '
            f'파일 {uploaded}개 업로드, 이미 사진 있음 {skipped}건'
        ))

    @staticmethod
    def _source_path(url):
        """정적 URL 에 해당하는 원본 파일. 없으면 None."""
        from equipment.photos import _IMAGES_ROOT

        marker = '/images/records/'
        if marker not in url:
            return None
        relative = url.split(marker, 1)[1]
        path = _IMAGES_ROOT / 'records' / relative
        return path if path.is_file() else None

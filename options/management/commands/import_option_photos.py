"""옵션 장치 초기 데이터를 넣는다 — 배포마다 실행된다.

사진은 ``static/images/options/<섹션 순서>/<번호>.jpg``로 커밋돼 있고, 여기서
저장소(운영은 R2)로 올린 뒤 행을 만든다. 카탈로그 PDF에서 뽑은 사진이라
문구·칸 이름도 그 지면 그대로다.

멱등이다. 이미 있는 섹션은 건드리지 않고, 저장소에 있는 파일은 다시 올리지
않는다. 직원이 어드민에서 사진을 손수 바꾼 섹션은 통째로 건너뛴다 —
equipment 쪽에서 라이브러리와 직접 올린 사진이 겹쳐 갤러리가 두 벌로 보이던
일이 있었다.
"""
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from PIL import Image

from equipment.imaging import encode_webp, webp_name
from options.models import OptionDevice, OptionPhoto


def measure(path):
    """원본 파일의 (가로, 세로). 저장된 사본은 열지 않는다 — 운영에서는 R2 왕복이다."""
    with Image.open(path) as im:
        return im.size

# 이 명령이 올리는 파일은 전부 이 아래. 바깥 경로는 어드민 업로드다
# (ImageField upload_to가 'options/'라 options/<원본파일명>으로 떨어진다).
DESIGN_PREFIX = 'options/design/'

# (순서, 장치명, 설명, 보조 문구, [(파일 번호, 칸 이름, 칸 위 작은 라벨, 사진 위 설명)])
SEED = [
    (1, '작업대 보호장치',
     '작업 중 공구 및 자재 낙하를 방지합니다.',
     '',
     [(0, '철망/메쉬망 보양', '장착 A타입', ''),
      (1, '함석 보양', '장착 B타입', '')]),
    # 카탈로그 지면에는 측면 사진도 함께 실려 있지만 빼두었다. 보양재 섹션과
    # 같은 장비를 자른 것이라 정작 협착방지장치가 보이지 않는다. 남긴 두 장은
    # 위에서 내려다본 사진으로, 난간의 버섯 모양 가드가 그대로 드러난다.
    (2, '협착방지장치',
     '작업자가 상부에 충돌하거나 끼이는 사고를 방지합니다.',
     '',
     [(0, 'A타입', '', ''),
      (2, 'A타입', '', '측면사진'),
      (1, 'B타입', '', ''),
      (3, 'B타입', '', '측면사진')]),
    (3, '라인빔',
     '라인빔을 이용하여 장비 주변의 안전반경을 표시합니다.',
     '',
     [(0, '장착 사례 A', '', ''),
      (1, '장착 사례 B', '', '')]),
]


class Command(BaseCommand):
    help = '옵션 장치 초기 데이터와 사진을 등록합니다.'

    def handle(self, *args, **options):
        root = settings.BASE_DIR / 'static' / 'images' / 'options'
        uploaded = devices_created = photos_created = skipped = relabelled = 0

        for order, title, lead, note, shots in SEED:
            device, created = OptionDevice.objects.get_or_create(
                title=title,
                defaults={'lead': lead, 'note': note, 'order': order},
            )
            if created:
                devices_created += 1
            elif (device.lead, device.note) != (lead, note):
                # 사진 문구와 같은 이유로 여기 적힌 값이 기준이다. get_or_create 의
                # defaults 는 만들 때만 쓰이므로, 위를 고쳐도 이미 있는 섹션에는
                # 닿지 않는다 — 어드민에서 같은 값을 손으로 또 고쳐야 했다.
                device.lead, device.note = lead, note
                device.save(update_fields=['lead', 'note'])
                relabelled += 1

            # 직접 올린 사진이 하나라도 있으면 이 섹션은 사람이 관리 중이다.
            if device.photos.exclude(image__startswith=DESIGN_PREFIX).exists():
                self.stdout.write(f'  · {title}: 직접 올린 사진이 있어 건너뜁니다')
                continue

            for index, (n, label, tag, caption) in enumerate(shots):
                source = root / str(order) / f'{n}.jpg'
                if not source.is_file():
                    self.stderr.write(self.style.WARNING(f'  ! 파일 없음: {source}'))
                    continue
                name = webp_name(f'{DESIGN_PREFIX}{order}/{n}.jpg')
                exists = OptionPhoto.objects.filter(device=device, image=name).first()
                if exists:
                    # 여기 적힌 문구가 이 사진들의 기준이다. 위에서 라벨을 고치면
                    # 이미 등록된 사진에도 반영돼야 하고, 그러지 않으면 문구를
                    # 바꿀 때마다 어드민에서 같은 값을 손으로 또 고쳐야 한다.
                    fields = []
                    if (exists.column_label, exists.column_tag, exists.caption) != (label, tag, caption):
                        exists.column_label, exists.column_tag = label, tag
                        exists.caption = caption
                        fields += ['column_label', 'column_tag', 'caption']
                    # 치수 필드가 생기기 전에 등록된 행은 비어 있다. 원본에서
                    # 재서 채운다 — 저장된 파일을 열면 운영에서는 R2 왕복이다.
                    if not exists.image_width:
                        exists.image_width, exists.image_height = measure(source)
                        fields += ['image_width', 'image_height']
                    if fields:
                        exists.save(update_fields=fields)
                        relabelled += 1
                    skipped += 1
                    continue
                if not default_storage.exists(name):
                    data, _ = encode_webp(source.read_bytes())
                    default_storage.save(name, ContentFile(data))
                    uploaded += 1
                width, height = measure(source)
                photo = OptionPhoto(device=device, image=name, column_label=label,
                                    column_tag=tag, caption=caption, order=index,
                                    image_width=width, image_height=height)
                # image 는 이미 저장소에 있는 경로다. save() 의 변환기를 태우면
                # 이름이 upload_to 를 한 번 더 거쳐 경로가 중첩된다.
                super(OptionPhoto, photo).save()
                photos_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'옵션 장치: 섹션 {devices_created}개 생성, 사진 {photos_created}개 등록, '
            f'파일 {uploaded}개 업로드, 문구 갱신 {relabelled}개, 이미 있음 {skipped}개'
        ))

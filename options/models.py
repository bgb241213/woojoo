"""옵션 장치 — 렌탈 장비에 부착해 드리는 부가 안전장치 안내.

카탈로그가 그렇듯 한 섹션은 좌우 비교로 읽힌다. 칸 수를 필드로 못 박는 대신
사진마다 칸 이름을 적게 하고, 같은 이름끼리 한 칸으로 묶는다. 칸이 둘이든
셋이든, 한 칸에 사진이 하나든 넷이든 그대로 받는다 — 실제로 협착방지장치는
칸마다 두 장(측면·평면)이다.
"""
from django.db import models


class OptionDevice(models.Model):
    title     = models.CharField(max_length=100, verbose_name='장치명',
                                 help_text='예: 작업대 보호장치')
    lead      = models.CharField(max_length=200, verbose_name='설명',
                                 help_text='이 장치가 무엇을 막아주는지 한 문장으로.')
    note      = models.CharField(max_length=200, blank=True, verbose_name='보조 문구',
                                 help_text='선택. 예: 철망/메쉬망 및 함석 부착 예시')
    order     = models.PositiveIntegerField(default=0, verbose_name='순서')
    is_active = models.BooleanField(default=True, verbose_name='노출 여부')

    class Meta:
        verbose_name = '옵션 장치'
        verbose_name_plural = '옵션 장치'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

    def columns(self):
        """[(칸 이름, 작은 라벨, [사진…])] — 칸 이름이 같은 사진끼리 묶는다.

        묶는 순서는 사진 순서를 따르므로, 어드민에서 사진 순서만 맞추면 칸
        순서도 따라온다.

        상자 모양은 사진마다가 아니라 **줄마다** 하나로 맞춘다. 나란히 놓고
        비교하는 화면이라 같은 줄의 상자 높이가 어긋나면 읽기 나쁘다. 한 줄에
        위에서 내려다본 세로 사진과 옆에서 찍은 가로 사진이 섞이지도 않는다 —
        섞이는 건 줄이 다른 경우다.
        """
        grouped = []
        index = {}
        for photo in self.photos.all():
            key = photo.column_label
            if key not in index:
                index[key] = len(grouped)
                grouped.append({'label': key, 'tag': photo.column_tag, 'photos': []})
            grouped[index[key]]['photos'].append(photo)

        depth = max((len(c['photos']) for c in grouped), default=0)
        for row in range(depth):
            shots = [c['photos'][row] for c in grouped if row < len(c['photos'])]
            ratios = [s.ratio for s in shots if s.ratio]
            # 가장 세로로 긴 사진에 맞춘다. 그보다 납작한 사진은 남는 자리가
            # 여백으로 갈 뿐, 어느 사진도 잘리지 않는다.
            box = min(ratios) if ratios else 0.75
            for s in shots:
                s.box_ratio = round(box, 4)
        return grouped


class OptionPhoto(models.Model):
    device       = models.ForeignKey(OptionDevice, on_delete=models.CASCADE,
                                     related_name='photos', verbose_name='옵션 장치')
    column_label = models.CharField(max_length=100, verbose_name='칸 이름',
                                    help_text='같은 칸에 넣을 사진은 이름을 똑같이 적으세요. '
                                              '예: 철망/메쉬망 보양')
    column_tag   = models.CharField(max_length=50, blank=True, verbose_name='칸 위 작은 라벨',
                                    help_text='선택. 예: 장착 A type — 칸의 첫 사진 값만 쓰입니다.')
    caption      = models.CharField(max_length=100, blank=True, verbose_name='사진 위 설명',
                                    help_text='선택. 사진 바로 위에 붙습니다. 예: 자세한 사진')
    image        = models.ImageField(upload_to='options/', verbose_name='사진',
                                     width_field='image_width', height_field='image_height')
    # 사진 비율로 상자 모양을 정하는데, 그때마다 파일을 열면 운영에서는 R2 를
    # 왕복한다. 저장할 때 한 번 재서 넣어 두고 화면에서는 숫자만 쓴다.
    image_width  = models.PositiveIntegerField(null=True, blank=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    order        = models.PositiveIntegerField(default=0, verbose_name='순서')

    class Meta:
        verbose_name = '옵션 장치 사진'
        verbose_name_plural = '옵션 장치 사진'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.device.title} - {self.column_label}'

    @property
    def ratio(self):
        """가로/세로. 치수가 아직 안 채워진 예전 행은 None."""
        if self.image_width and self.image_height:
            return self.image_width / self.image_height
        return None

    def save(self, *args, **kwargs):
        """새로 올라온 사진만 WebP로 줄인다 — equipment/imaging.py 참고.

        이미 저장된 파일에 다시 걸면 이름이 upload_to를 한 번 더 거쳐
        디렉터리가 중첩되므로, 파일이 바뀐 경우에만 손댄다.
        """
        from equipment.imaging import compress_upload

        changed = self.pk is None
        if not changed:
            previous = OptionPhoto.objects.filter(pk=self.pk).values_list('image', flat=True).first()
            changed = previous != self.image.name
        if changed and self.image:
            compress_upload(self.image)
        super().save(*args, **kwargs)


# ── 어드민에서 지운 사진은 저장소(R2)에서도 지운다 ──
from django.db.models.signals import post_delete, pre_save  # noqa: E402
from django.dispatch import receiver  # noqa: E402


@receiver(post_delete, sender=OptionPhoto)
def _option_photo_deleted(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_save, sender=OptionPhoto)
def _option_photo_replaced(sender, instance, **kwargs):
    """사진을 교체하면 옛 파일은 남겨둘 이유가 없다."""
    if not instance.pk:
        return
    try:
        old = OptionPhoto.objects.get(pk=instance.pk)
    except OptionPhoto.DoesNotExist:
        return
    if old.image and old.image.name != instance.image.name:
        old.image.delete(save=False)

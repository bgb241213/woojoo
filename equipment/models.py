from django.db import models


class Equipment(models.Model):
    # Order matters: this is the catalog order used across the site.
    CATEGORY_CHOICES = [
        ('5m',       '1인승'),
        ('6m',       '미니(6M급)'),
        ('7m',       '7M급'),
        ('8m',       '8M급'),
        ('10m',      '10M급'),
        ('12m',      '12M급'),
        ('14m',      '14M급'),
        ('16m',      '16M급'),
        ('etc',      '기타장비'),
    ]

    TYPE_CHOICES = [
        ('scissor',  '시저'),
        ('boom',     '굴절'),
        ('vertical', '버티칼'),
        ('other',    '기타'),
    ]

    name                = models.CharField(max_length=100, verbose_name='모델명')
    category            = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='미터급')
    type                = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='타입')
    image               = models.ImageField(upload_to='equipment/', blank=True, null=True, verbose_name='장비 사진')
    description         = models.TextField(blank=True, verbose_name='장비 설명')
    max_work_height     = models.CharField(max_length=50, verbose_name='작업가능높이')
    max_platform_height = models.CharField(max_length=50, verbose_name='발판최대높이')
    equipment_weight    = models.CharField(max_length=50, verbose_name='장비무게')
    max_load            = models.CharField(max_length=50, verbose_name='적재가능중량')
    equipment_size      = models.CharField(max_length=100, verbose_name='장비크기')
    platform_size       = models.CharField(max_length=100, verbose_name='작업대크기')
    power_type          = models.CharField(max_length=50, verbose_name='동력')
    is_active           = models.BooleanField(default=True, verbose_name='노출 여부')
    # Rental and sale listings are independent — a machine can appear on both.
    is_for_rent         = models.BooleanField(default=True, verbose_name='렌탈 노출')
    is_for_sale         = models.BooleanField(default=False, verbose_name='판매 노출')
    # Pinned to the top of its meter class on every listing.
    is_flagship         = models.BooleanField(default=False, verbose_name='대표장비')
    # Opens the landing page's "많이 찾는 장비" list, ahead of meter order —
    # that section leads with what actually rents most, not with the smallest
    # machine. A flag rather than a hardcoded model name so it moves from the
    # admin when the best seller changes.
    is_bestseller       = models.BooleanField(
        default=False, verbose_name='최다 문의 장비',
        help_text='랜딩 페이지 "많이 찾는 장비" 목록 맨 앞에 나옵니다. '
                  '보통 한 대만 체크합니다.',
    )
    created_at          = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = '장비'
        verbose_name_plural = '장비 목록'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class EquipmentImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('rental',  '렌탈용'),
        ('sales',   '판매용'),
        ('compare', '비교용'),
    ]

    equipment  = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='images', verbose_name='장비')
    image      = models.ImageField(upload_to='equipment/', verbose_name='이미지')
    image_type = models.CharField(max_length=10, choices=IMAGE_TYPE_CHOICES, verbose_name='이미지 용도')
    order      = models.PositiveIntegerField(default=0, verbose_name='순서')
    # Two separate numbers on purpose: `baseline_detected` is refreshed by the
    # machine every time the file changes, `baseline` is what a human typed and
    # must never be overwritten. See equipment/baseline.py.
    baseline_detected = models.FloatField(
        null=True, blank=True, verbose_name='바퀴선 자동 인식값(%)',
        help_text='사진을 올리면 시스템이 바퀴가 땅에 닿는 위치를 자동으로 찾아 채웁니다. '
                  '직접 고칠 필요는 없습니다.',
    )
    baseline   = models.FloatField(
        null=True, blank=True, verbose_name='바퀴선 직접 지정(%)',
        help_text='비워두면 위의 자동 인식값을 사용합니다. 장비 비교 페이지에서 '
                  '이 장비만 바퀴 높이가 어긋나 보일 때에만 숫자를 입력하세요. '
                  '(사진 맨 아래에서 바퀴까지의 높이 비율, 예: 4.2)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '장비 사진'
        verbose_name_plural = '장비 사진'
        ordering = ['order']

    def __str__(self):
        return f'{self.equipment.name} - {self.get_image_type_display()} ({self.order})'

    @property
    def effective_baseline(self):
        """The number the compare page should use: manual wins over detected."""
        return self.baseline if self.baseline is not None else self.baseline_detected

    # Set on an instance to suppress the save-time detection below, for callers
    # that already know the value. Bulk importers must use it: detection reads
    # the file back out of storage, and doing that per row turned a deploy into
    # a hundred R2 round-trips and timed out the healthcheck.
    skip_baseline_detection = False

    def save(self, *args, **kwargs):
        """Compress to WebP and re-detect the wheel line when the file changes.

        Detection reads the file, which is a network round-trip to R2 in
        production — so both steps only run when the file is actually new or
        replaced, never on an ordinary edit of the order/type fields.
        """
        from .baseline import detect_percent_for_file
        from .imaging import compress_upload

        changed = self.pk is None
        if not changed:
            previous = EquipmentImage.objects.filter(pk=self.pk).values_list('image', flat=True).first()
            changed = previous != self.image.name
        # Convert before the file lands in storage, so R2 never holds the
        # multi-megabyte original and no second pass is needed later.
        if changed and self.image:
            compress_upload(self.image)
        super().save(*args, **kwargs)
        if changed and self.image and not self.skip_baseline_detection:
            detected = detect_percent_for_file(self.image)
            if detected != self.baseline_detected:
                EquipmentImage.objects.filter(pk=self.pk).update(baseline_detected=detected)
                self.baseline_detected = detected


# ── Keep the storage backend (R2 in production) in sync with the admin ──
from django.db.models.signals import post_delete, pre_save  # noqa: E402
from django.dispatch import receiver  # noqa: E402


@receiver(post_delete, sender=EquipmentImage)
def _equipment_image_deleted(sender, instance, **kwargs):
    """Deleting a row in the admin also removes the file from storage."""
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_save, sender=EquipmentImage)
def _equipment_image_replaced(sender, instance, **kwargs):
    """Replacing a file in the admin removes the old object from storage."""
    if not instance.pk:
        return
    try:
        old = EquipmentImage.objects.get(pk=instance.pk)
    except EquipmentImage.DoesNotExist:
        return
    if old.image and old.image.name != instance.image.name:
        old.image.delete(save=False)

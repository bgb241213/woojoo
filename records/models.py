from django.db import models
from django.utils import timezone


class SalesRecord(models.Model):
    """판매 실적 벽의 사진 한 장.

    한 행이 곧 한 장이다. 사진을 올리고 그 사진에 붙는 정보를 적어 저장하면
    그대로 벽의 타일 하나가 된다 — 실적 하나에 사진 여러 장을 매다는 구조는
    어드민에서 어느 사진이 어느 정보에 해당하는지 알 수 없어 접었다.

    처음 사진은 ``static/images/records/<photo_key>/`` 라이브러리에서
    ``import_record_photos`` 가 옮겨 왔다.
    """
    image        = models.ImageField(upload_to='records/', blank=True, verbose_name='사진')
    model_name   = models.CharField(max_length=100, blank=True, verbose_name='모델명')
    # 화면에 나오지 않는 값인데 사진을 올릴 때마다 손으로 적어야 했다.
    # 오늘 날짜로 채워두면 그대로 저장해도 되고, 지난 건이면 고치면 된다.
    shipped_date = models.DateField(default=timezone.localdate, verbose_name='출고일')
    photo_key    = models.PositiveIntegerField(null=True, blank=True,
                                               verbose_name='사진 폴더 ID',
                                               help_text='처음 사진을 불러온 폴더 번호입니다. 비워두셔도 됩니다.')
    is_active    = models.BooleanField(default=True, verbose_name='노출 여부')
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = '판매 실적'
        verbose_name_plural = '판매 실적 목록'
        ordering = ['-shipped_date', '-id']

    def __str__(self):
        return f'{self.model_name or "고소작업대"} ({self.shipped_date})'

    def photo_url(self):
        """벽에 걸리는 사진 주소. 파일이 없으면 None."""
        if self.image:
            try:
                return self.image.url
            except ValueError:
                pass
        return None

    def save(self, *args, **kwargs):
        """새로 올라온 사진만 WebP로 줄인다 — equipment/imaging.py 참고.

        이미 저장된 파일에 다시 걸면 이름이 upload_to 를 한 번 더 거쳐
        디렉터리가 중첩되므로, 파일이 바뀐 경우에만 손댄다.
        """
        from equipment.imaging import compress_upload

        changed = self.pk is None
        if not changed:
            previous = SalesRecord.objects.filter(pk=self.pk).values_list('image', flat=True).first()
            changed = previous != self.image.name
        if changed and self.image:
            compress_upload(self.image)
        super().save(*args, **kwargs)


# ── 어드민에서 지운 사진은 저장소(R2)에서도 지운다 ──
from django.db.models.signals import post_delete, pre_save  # noqa: E402
from django.dispatch import receiver  # noqa: E402


@receiver(post_delete, sender=SalesRecord)
def _record_deleted(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_save, sender=SalesRecord)
def _record_image_replaced(sender, instance, **kwargs):
    """사진을 교체하면 옛 파일은 남겨둘 이유가 없다."""
    if not instance.pk:
        return
    try:
        old = SalesRecord.objects.get(pk=instance.pk)
    except SalesRecord.DoesNotExist:
        return
    if old.image and old.image.name != instance.image.name:
        old.image.delete(save=False)

from django.db import models


class SalesRecord(models.Model):
    """A shipment record shown on the 판매 실적 wall.

    Imported records reuse the Claude Design photo library committed under
    ``static/images/records/<photo_key>/``. Records added later through the
    admin attach their own uploaded ``SalesRecordImage`` rows instead.
    """
    model_name   = models.CharField(max_length=100, blank=True, verbose_name='모델명')
    shipped_date = models.DateField(verbose_name='출고일')
    photo_key    = models.PositiveIntegerField(null=True, blank=True, unique=True,
                                               verbose_name='사진 폴더 ID',
                                               help_text='static/images/records/<ID>/ 폴더 번호 (임포트 데이터용)')
    is_active    = models.BooleanField(default=True, verbose_name='노출 여부')
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = '판매 실적'
        verbose_name_plural = '판매 실적 목록'
        ordering = ['-shipped_date', '-id']

    def __str__(self):
        return f'{self.model_name or "고소작업대"} ({self.shipped_date})'

    def photo_urls(self):
        """Photo URLs for this record (admin uploads take priority)."""
        uploaded = [img.image.url for img in self.images.all()]
        if uploaded:
            return uploaded
        if self.photo_key:
            from equipment.photos import record_photos
            return record_photos(self.photo_key)
        return []


class SalesRecordImage(models.Model):
    record = models.ForeignKey(SalesRecord, on_delete=models.CASCADE, related_name='images', verbose_name='실적')
    image  = models.ImageField(upload_to='records/', verbose_name='사진')
    order  = models.PositiveIntegerField(default=0, verbose_name='순서')

    class Meta:
        verbose_name = '실적 사진'
        verbose_name_plural = '실적 사진 목록'
        ordering = ['order']

    def __str__(self):
        return f'{self.record} - {self.order}'

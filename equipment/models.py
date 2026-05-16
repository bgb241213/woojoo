from django.db import models


class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ('5m',       '5M급'),
        ('6m',       '6M급'),
        ('7m',       '7M급'),
        ('8m',       '8M급'),
        ('10m',      '10M급'),
        ('12m',      '12M급'),
        ('14m',      '14M급'),
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
    is_for_sale         = models.BooleanField(default=False, verbose_name='판매 가능')
    created_at          = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = '장비'
        verbose_name_plural = '장비 목록'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class EquipmentImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('rental', '렌탈용'),
        ('sales',  '판매용'),
    ]

    equipment  = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='images', verbose_name='장비')
    image      = models.ImageField(upload_to='equipment/', verbose_name='이미지')
    image_type = models.CharField(max_length=10, choices=IMAGE_TYPE_CHOICES, verbose_name='이미지 용도')
    order      = models.PositiveIntegerField(default=0, verbose_name='순서')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '장비 이미지'
        verbose_name_plural = '장비 이미지 목록'
        ordering = ['order']

    def __str__(self):
        return f'{self.equipment.name} - {self.get_image_type_display()} ({self.order})'

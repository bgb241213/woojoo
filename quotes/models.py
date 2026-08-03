from django.db import models
from equipment.models import Equipment


class QuoteRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',    '대기'),
        ('reviewing',  '검토중'),
        ('completed',  '완료'),
        ('cancelled',  '취소'),
    ]

    INQUIRY_TYPE_CHOICES = [
        ('rental',    '렌탈'),
        ('sale',      '판매'),
        ('undecided', '미정'),
    ]

    company_name     = models.CharField(max_length=200, blank=True, verbose_name='회사명')
    name             = models.CharField(max_length=100, blank=True, verbose_name='담당자명')
    phone            = models.CharField(max_length=20, verbose_name='연락처')
    email            = models.EmailField(blank=True, verbose_name='이메일')
    business_number  = models.CharField(max_length=20, blank=True, verbose_name='사업자번호')
    inquiry_type     = models.CharField(max_length=20, choices=INQUIRY_TYPE_CHOICES, default='rental', blank=True, verbose_name='구분')
    work_height_class = models.CharField(max_length=20, blank=True, verbose_name='필요 작업고')
    start_date       = models.DateField(null=True, blank=True, verbose_name='렌탈 시작일')
    end_date         = models.DateField(null=True, blank=True, verbose_name='렌탈 종료일')
    delivery_address = models.TextField(blank=True, verbose_name='현장 주소')
    budget           = models.PositiveIntegerField(null=True, blank=True, verbose_name='예산')
    message          = models.TextField(blank=True, verbose_name='추가 요청사항')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='상태')
    # Recorded so the company can evidence lawful collection if it is ever
    # questioned — a checkbox in the UI alone proves nothing after the fact.
    privacy_agreed_at = models.DateTimeField(null=True, blank=True, verbose_name='개인정보 수집·이용 동의일시')
    created_at       = models.DateTimeField(auto_now_add=True, verbose_name='신청일')

    class Meta:
        verbose_name = '견적 신청'
        verbose_name_plural = '견적 신청 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.company_name} - {self.name} ({self.created_at.strftime("%Y-%m-%d")})'


class CallbackRequest(models.Model):
    phone      = models.CharField(max_length=20, verbose_name='전화번호')
    message    = models.TextField(blank=True, verbose_name='문의 내용')
    is_called  = models.BooleanField(default=False, verbose_name='전화 완료')
    privacy_agreed_at = models.DateTimeField(null=True, blank=True, verbose_name='개인정보 수집·이용 동의일시')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='신청일시')

    class Meta:
        verbose_name = '콜백 신청'
        verbose_name_plural = '콜백 신청 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone} ({self.created_at.strftime("%Y-%m-%d %H:%M")})'


class QuoteItem(models.Model):
    quote     = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, related_name='items', verbose_name='견적')
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, verbose_name='장비')
    quantity  = models.PositiveIntegerField(verbose_name='수량')

    class Meta:
        verbose_name = '견적 장비'
        verbose_name_plural = '견적 장비 목록'

    def __str__(self):
        return f'{self.equipment.name} x {self.quantity}'

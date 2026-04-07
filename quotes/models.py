from django.db import models
from equipment.models import Equipment


class QuoteRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',    '대기'),
        ('reviewing',  '검토중'),
        ('completed',  '완료'),
        ('cancelled',  '취소'),
    ]

    company_name     = models.CharField(max_length=200, verbose_name='회사명')
    name             = models.CharField(max_length=100, verbose_name='담당자명')
    phone            = models.CharField(max_length=20, verbose_name='연락처')
    email            = models.EmailField(verbose_name='이메일')
    business_number  = models.CharField(max_length=20, blank=True, verbose_name='사업자번호')
    start_date       = models.DateField(verbose_name='렌탈 시작일')
    end_date         = models.DateField(verbose_name='렌탈 종료일')
    delivery_address = models.TextField(verbose_name='배송지 주소')
    budget           = models.PositiveIntegerField(null=True, blank=True, verbose_name='예산')
    message          = models.TextField(blank=True, verbose_name='추가 요청사항')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='상태')
    created_at       = models.DateTimeField(auto_now_add=True, verbose_name='신청일')

    class Meta:
        verbose_name = '견적 신청'
        verbose_name_plural = '견적 신청 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.company_name} - {self.name} ({self.created_at.strftime("%Y-%m-%d")})'


class QuoteItem(models.Model):
    quote     = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, related_name='items', verbose_name='견적')
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, verbose_name='장비')
    quantity  = models.PositiveIntegerField(verbose_name='수량')

    class Meta:
        verbose_name = '견적 장비'
        verbose_name_plural = '견적 장비 목록'

    def __str__(self):
        return f'{self.equipment.name} x {self.quantity}'

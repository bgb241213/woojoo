"""옵션 장치 어드민.

화면이 좌우 비교로 읽히므로 어드민도 그 구조를 그대로 보여준다: 먼저 칸을
만들고, 사진은 그 칸을 고른다.

전에는 사진마다 칸 이름을 손으로 적었다. 한 글자만 달라도 칸이 조용히
갈라졌고, 어드민은 그렇다고 말해 주지 않았다. 이제 이 화면에서 오타로 깨질 수
있는 곳은 없다 — 고르는 것만 남겼다.
"""
from django.contrib import admin
from django.db.models import ImageField
from django.utils.html import format_html

from equipment.admin_actions import RowActionsMixin
from equipment.admin_widgets import PhotoInput

from .models import OptionColumn, OptionDevice, OptionPhoto

_THUMB = ('height:{}px;width:auto;border-radius:6px;border:1px solid #dee2e6;'
          'background:#fff;object-fit:contain;')


def _thumb(url, height):
    return format_html('<img src="{}" style="' + _THUMB.format(height) + '" />', url)


def _muted(text):
    return format_html('<span style="color:#9296a8;">{}</span>', text)


class OptionColumnInline(admin.TabularInline):
    model = OptionColumn
    extra = 1
    fields = ['label', 'tag', 'order', 'photo_count']
    readonly_fields = ['photo_count']
    verbose_name = '칸'
    verbose_name_plural = ('① 칸 — 화면에서 좌우로 놓일 칸입니다. '
                           '여기서 만들고 저장하면 아래 사진에서 고를 수 있습니다')

    @admin.display(description='붙은 사진')
    def photo_count(self, obj):
        if not obj.pk:
            return _muted('저장하면 셉니다')
        count = obj.photos.count()
        if not count:
            return format_html('<span style="color:#c62828;">아직 없음</span>')
        return format_html('<b>{}</b>장', count)


class OptionPhotoInline(admin.TabularInline):
    model = OptionPhoto
    extra = 2
    fields = ['preview', 'image', 'column', 'caption', 'order']
    readonly_fields = ['preview']
    verbose_name = '사진'
    verbose_name_plural = '② 사진 — 사진을 고르고, 어느 칸에 넣을지만 정하면 됩니다'

    formfield_overrides = {ImageField: {'widget': PhotoInput}}

    @admin.display(description='미리보기')
    def preview(self, obj):
        if obj.pk and obj.image:
            try:
                return _thumb(obj.image.url, 96)
            except ValueError:
                pass
        return _muted('저장하면 보입니다')

    def get_formset(self, request, obj=None, **kwargs):
        # 칸 목록을 이 장치 것으로만 좁히려면 지금 편집 중인 장치를 알아야 한다.
        self._device = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'column':
            device = getattr(self, '_device', None)
            kwargs['queryset'] = (OptionColumn.objects.filter(device=device)
                                  if device else OptionColumn.objects.none())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(OptionDevice)
class OptionDeviceAdmin(RowActionsMixin, admin.ModelAdmin):
    list_display = ['thumb', 'title', 'column_summary', 'order',
                    'active_toggle', 'row_delete']
    list_display_links = ['thumb', 'title']
    list_editable = ['order']
    list_filter = ['is_active']
    search_fields = ['title', 'lead']
    ordering = ['order', 'id']
    save_on_top = True
    inlines = [OptionColumnInline, OptionPhotoInline]

    fieldsets = (
        ('내용', {
            'fields': ('title', 'lead', 'note'),
            'description': '장치명은 섹션 제목으로, 설명은 그 아래 한 줄로 나갑니다. '
                           '보조 문구는 비워두셔도 됩니다.',
        }),
        ('노출 설정', {
            'fields': ('order', 'is_active'),
            'description': '순서가 작을수록 페이지 위쪽에 나옵니다. '
                           '노출을 끄면 페이지에서 사라집니다.',
        }),
    )

    @admin.display(description='사진')
    def thumb(self, obj):
        first = OptionPhoto.objects.filter(column__device=obj).order_by('order', 'id').first()
        if first and first.image:
            try:
                return _thumb(first.image.url, 44)
            except ValueError:
                pass
        return _muted('없음')

    @admin.display(description='칸 구성')
    def column_summary(self, obj):
        columns = list(obj.columns_set.all())
        if not columns:
            return format_html('<span style="color:#c62828;">칸 없음</span>')
        parts = []
        for col in columns:
            count = len(col.photos.all())
            parts.append(f'{col.label} ({count}장)' if count else f'{col.label} (사진 없음)')
        return ' · '.join(parts)

    def get_queryset(self, request):
        # column_summary/thumb 가 행마다 사진 테이블을 두드리지 않도록.
        return super().get_queryset(request).prefetch_related('columns_set__photos')

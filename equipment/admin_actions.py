"""목록 한 줄에서 바로 하는 일 — 노출 켜고 끄기, 삭제.

체크박스로 노출을 바꾸려면 체크를 하고 목록 아래 저장까지 눌러야 했다. 저장을
잊으면 아무 일도 일어나지 않는데 화면은 바뀐 것처럼 보여서, 껐다고 생각한 장비가
그대로 홈페이지에 남았다.

여기서는 버튼 하나가 곧 한 번의 저장이다. 누르면 그 자리에서 바뀌고 글자도
"노출 안 하기" ↔ "노출하기" 로 뒤집힌다. 저장할 것이 남지 않는다.

삭제도 같은 이유로 줄에 붙였다. 체크하고, 위로 올라가 동작을 고르고, 실행을
누르는 세 단계는 한 대를 지우려는 사람에게는 길다. 다만 삭제는 되돌릴 수 없으니
버튼이 그 자리에서 지우지는 않는다 — 장고가 이미 갖고 있는 확인 화면으로 보낸다.
무엇이 함께 사라지는지(장비라면 그 사진들) 거기서 보여준다.

쓰려면 ModelAdmin 에 섞고 list_display 에 ``active_toggle`` 과 ``row_delete`` 를
넣으면 된다. ``list_editable`` 은 함께 쓰지 않는다 — 같은 값을 두 곳에서
바꾸게 된다.
"""
from django.contrib import admin
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from django.views.decorators.http import require_POST


class RowActionsMixin:
    """목록 한 줄에 붙는 노출 버튼과 삭제 버튼."""

    active_field = 'is_active'
    active_on_label = '노출 안 하기'   # 지금 켜져 있을 때 누를 버튼
    active_off_label = '노출하기'      # 지금 꺼져 있을 때 누를 버튼

    def get_urls(self):
        meta = self.model._meta
        name = f'{meta.app_label}_{meta.model_name}_toggle_active'
        return [
            path('<int:pk>/toggle-active/',
                 self.admin_site.admin_view(require_POST(self.toggle_active)),
                 name=name),
        ] + super().get_urls()

    def toggle_active(self, request, pk):
        obj = get_object_or_404(self.model, pk=pk)
        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        value = not getattr(obj, self.active_field)
        setattr(obj, self.active_field, value)
        obj.save(update_fields=[self.active_field])

        # 어드민 기록에 남겨야 "누가 이걸 껐지" 를 나중에 찾을 수 있다.
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.model).pk,
            object_id=obj.pk,
            object_repr=str(obj),
            action_flag=CHANGE,
            change_message='노출함' if value else '노출 안 함',
        )
        return JsonResponse({
            'active': value,
            'label': self.active_on_label if value else self.active_off_label,
        })

    @admin.display(description='홈페이지 노출')
    def active_toggle(self, obj):
        meta = self.model._meta
        url = reverse(f'admin:{meta.app_label}_{meta.model_name}_toggle_active',
                      args=[obj.pk])
        active = getattr(obj, self.active_field)
        return format_html(
            '<button type="button" class="wj-toggle{}" data-toggle-url="{}" '
            'data-label-on="{}" data-label-off="{}">{}</button>',
            '' if active else ' is-off', url,
            self.active_on_label, self.active_off_label,
            self.active_on_label if active else self.active_off_label,
        )

    @admin.display(description='삭제')
    def row_delete(self, obj):
        """장고의 삭제 확인 화면으로 보내는 링크.

        여기서 바로 지우지 않는 것이 요점이다. 확인 화면은 무엇이 함께
        사라지는지 보여주고 한 번 더 묻는다 — 되돌릴 수 없는 동작에 필요한
        단계다.
        """
        meta = self.model._meta
        url = reverse(f'admin:{meta.app_label}_{meta.model_name}_delete', args=[obj.pk])
        return format_html('<a class="wj-delete" href="{}">삭제</a>', url)

    def get_list_display(self, request):
        """지울 권한이 없는 계정에는 삭제 버튼을 보이지 않는다."""
        fields = super().get_list_display(request)
        if self.has_delete_permission(request):
            return fields
        return tuple(f for f in fields if f != 'row_delete')

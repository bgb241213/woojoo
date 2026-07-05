import json

from django.views.generic import ListView, View
from django.views.generic.base import RedirectView
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Equipment
from .photos import rental_photos, sale_photos

# Meter-class tab labels (6M급 covers the 5~6M range).
CATEGORY_LABEL = {
    '5m': '5M', '6m': '5~6M', '7m': '7M', '8m': '8M',
    '10m': '10M', '12m': '12M', '14m': '14M',
}

# Numeric ordering for meter classes (the stored keys sort wrong as strings).
CATEGORY_ORDER = {key: i for i, (key, _) in enumerate(Equipment.CATEGORY_CHOICES)}

# Spec rows shown on rental list cards, in display order.
RENTAL_SPECS = [
    ('작업 높이', 'max_work_height'),
    ('발판 높이', 'max_platform_height'),
    ('적재 중량', 'max_load'),
    ('동력', 'power_type'),
    ('장비 무게', 'equipment_weight'),
    ('장비 크기 (L×W×H)', 'equipment_size'),
    ('작업대 크기', 'platform_size'),
]


def decorate(equipment, photos, spec_fields):
    """Attach template-friendly photo/spec attributes to an Equipment instance."""
    equipment.photos = photos
    equipment.category_label = equipment.get_category_display()
    equipment.type_label = equipment.get_type_display()
    equipment.specs = [(label, getattr(equipment, field)) for label, field in spec_fields]
    return equipment


def meter_tabs(equipments):
    """Build [(key, label, count)] tabs for the meter-class selector."""
    counts = {}
    for e in equipments:
        counts[e.category] = counts.get(e.category, 0) + 1
    tabs = [('all', '전체', len(equipments))]
    for key, _ in Equipment.CATEGORY_CHOICES:
        if key in counts:
            tabs.append((key, CATEGORY_LABEL.get(key, key), counts[key]))
    return tabs


class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment/list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        qs = Equipment.objects.filter(is_active=True, is_for_sale=False)
        return [decorate(e, rental_photos(e.id), RENTAL_SPECS) for e in qs]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['meter_tabs'] = meter_tabs(ctx['equipments'])
        return ctx


class EquipmentDetailView(RedirectView):
    """The redesign shows full specs inline on the list; detail pages just
    deep-link into the rental list, anchored to the machine."""
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse('equipment:list') + f"#eq-{kwargs['pk']}"


class EquipmentCompareView(View):
    template_name = 'equipment/compare.html'

    def get(self, request):
        # Sort by meter class (5M→14M), then model name within each class.
        equipment = sorted(
            Equipment.objects.filter(is_active=True),
            key=lambda e: (CATEGORY_ORDER.get(e.category, 99), e.name),
        )
        models = []
        for e in equipment:
            models.append({
                'id': e.id,
                'name': e.name,
                'category': e.get_category_display(),
                'type': e.get_type_display(),
                'isForSale': e.is_for_sale,
                'photos': rental_photos(e.id) or sale_photos(e.id),
                'specs': {
                    '작업가능높이': e.max_work_height,
                    '발판최대높이': e.max_platform_height,
                    '적재가능중량': e.max_load,
                    '장비무게': e.equipment_weight,
                    '동력': e.power_type,
                    '장비크기': e.equipment_size,
                    '작업대크기': e.platform_size,
                },
            })
        return render(request, self.template_name, {
            'models_json': json.dumps(models, ensure_ascii=False),
        })


class EquipmentByCategoryAPI(View):
    def get(self, request):
        category = request.GET.get('category', '')
        qs = Equipment.objects.filter(is_active=True)
        if category:
            qs = qs.filter(category=category)
        data = [{'id': e.id, 'name': e.name} for e in qs]
        return JsonResponse({'equipments': data})

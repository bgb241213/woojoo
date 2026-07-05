from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.urls import reverse

from equipment.models import Equipment
from equipment.photos import sale_photos
from equipment.views import decorate, meter_tabs

# Spec rows shown on sale list cards, in display order.
SALE_SPECS = [
    ('작업 높이', 'max_work_height'),
    ('발판 높이', 'max_platform_height'),
    ('적재 중량', 'max_load'),
    ('장비 무게', 'equipment_weight'),
    ('동력', 'power_type'),
    ('장비 크기 (L×W×H)', 'equipment_size'),
    ('작업대 크기', 'platform_size'),
]


class SalesListView(ListView):
    template_name = 'sales/list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        qs = Equipment.objects.filter(is_for_sale=True, is_active=True)
        return [decorate(e, sale_photos(e.id), SALE_SPECS) for e in qs]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['meter_tabs'] = meter_tabs(ctx['equipments'])
        return ctx


class SalesDetailView(RedirectView):
    """Sale detail pages deep-link into the sale list, anchored to the machine."""
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse('sales:list') + f"#eq-{kwargs['pk']}"

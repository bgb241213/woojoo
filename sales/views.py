from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.urls import reverse

from equipment.models import Equipment
from equipment.photos import rental_photos, sale_photos
from equipment.views import decorate, meter_tabs

# Spec rows shown on sale list cards, in display order (Claude Design renewal).
SALE_SPECS = [
    ('작업가능높이', 'max_work_height'),
    ('발판최대높이', 'max_platform_height'),
    ('장비무게', 'equipment_weight'),
    ('적재가능중량', 'max_load'),
    ('장비크기', 'equipment_size'),
    ('작업대크기', 'platform_size'),
    ('동력', 'power_type'),
]


class SalesListView(ListView):
    template_name = 'sales/list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        qs = Equipment.objects.filter(is_for_sale=True, is_active=True)
        items = []
        for e in qs:
            e = decorate(e, sale_photos(e.id), SALE_SPECS)
            # Rental photos become extra carousel slides after the sale grid.
            e.rental_slides = rental_photos(e.id)
            items.append(e)
        return items

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['meter_tabs'] = meter_tabs(ctx['equipments'])
        return ctx


class SalesDetailView(RedirectView):
    """Sale detail pages deep-link into the sale list, anchored to the machine."""
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse('sales:list') + f"#eq-{kwargs['pk']}"

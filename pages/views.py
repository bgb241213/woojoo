from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.urls import reverse

from equipment.models import Equipment
from equipment.photos import rental_photos, PLACEHOLDER
from equipment.views import catalog_order


def flagship_index():
    """The landing page's equipment index — one representative machine per
    meter class, in catalog order, with its card photo."""
    items = []
    qs = Equipment.objects.filter(is_active=True, is_for_rent=True, is_flagship=True)
    for e in catalog_order(qs):
        photos = rental_photos(e.id)
        items.append({
            'name': e.name,
            'category': e.get_category_display(),
            'type': e.get_type_display(),
            'height': e.max_work_height,
            'photo': photos[0] if photos else PLACEHOLDER,
            'href': f"{reverse('equipment:list')}#cls-{e.category}",
        })
    return items


class HomeView(View):
    template_name = 'pages/index.html'

    def get(self, request):
        return render(request, self.template_name, {
            'flagships': flagship_index(),
        })


class AboutView(TemplateView):
    template_name = 'pages/about.html'

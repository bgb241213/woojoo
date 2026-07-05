import json
import re

from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.urls import reverse
from equipment.models import Equipment


def _parse_height(text):
    """Extract the leading numeric value from a spec string like '7.62m'."""
    m = re.search(r'-?\d+(\.\d+)?', text or '')
    return float(m.group()) if m else 0.0


def equipment_finder_data():
    """Serialisable equipment list used by the home-page work-height finder."""
    data = []
    for e in Equipment.objects.filter(is_active=True):
        target = 'sales:list' if e.is_for_sale else 'equipment:list'
        data.append({
            'id': e.id,
            'name': e.name,
            'category': e.get_category_display(),
            'type': e.get_type_display(),
            'isForSale': e.is_for_sale,
            'maxWorkHeight': _parse_height(e.max_work_height),
            'heightLabel': e.max_work_height,
            'platformLabel': e.max_platform_height,
            'loadLabel': e.max_load,
            'weightLabel': e.equipment_weight,
            'detailHref': f'{reverse(target)}#eq-{e.id}',
        })
    return data


class HomeView(View):
    template_name = 'pages/index.html'

    def get(self, request):
        return render(request, self.template_name, {
            'equipment_json': json.dumps(equipment_finder_data(), ensure_ascii=False),
            'hero_images': ['images/hero/hero1.jpeg', 'images/hero/hero2.jpeg', 'images/hero/hero3.jpeg'],
        })


class AboutView(TemplateView):
    template_name = 'pages/about.html'

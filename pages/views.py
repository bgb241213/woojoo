from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.urls import reverse

from equipment.models import Equipment
from equipment.photos import bulk_db_images, rental_photos, PLACEHOLDER
from equipment.views import catalog_order


def flagship_index():
    """The landing page's equipment index — one representative machine per
    meter class, in catalog order, with its card photo."""
    items = []
    machines = catalog_order(
        Equipment.objects.filter(is_active=True, is_for_rent=True, is_flagship=True)
    )
    # The section is "많이 찾는 장비", so it leads with the machine that actually
    # rents most rather than with the smallest meter class. Stable sort:
    # everything else keeps its catalog order.
    machines.sort(key=lambda e: not e.is_bestseller)
    rental = bulk_db_images([e.id for e in machines], 'rental')
    for e in machines:
        photos = rental_photos(e.id, rental)
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


# Business details the privacy policy has to disclose by law. Kept here rather
# than inline in the template so the CPO/contact details live in one place.
COMPANY = {
    'name':       '(주)우주렌탈',
    'ceo':        '박성조',
    'biz_number': '326-88-01739',
    'address':    '경기도 고양시 덕양구 호국로1254번길 130-5(신원동)',
    'phone':      '031-973-6661',
    'email':      'woojoo66666@daum.net',
    'cpo_name':   '박성조',
    'cpo_title':  '대표',
}

# Bump this whenever the policy text changes; it is shown as 시행일자 and the
# law requires notice 7 days before a change takes effect.
PRIVACY_EFFECTIVE_DATE = '2026년 8월 2일'


class PrivacyView(TemplateView):
    template_name = 'pages/privacy.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['company'] = COMPANY
        ctx['effective_date'] = PRIVACY_EFFECTIVE_DATE
        return ctx

from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Prefetch
from .models import Equipment, EquipmentImage


class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment/list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        category = self.request.GET.get('category')
        qs = Equipment.objects.filter(is_active=True).prefetch_related(
            Prefetch(
                'images',
                queryset=EquipmentImage.objects.filter(image_type='rental').order_by('order'),
                to_attr='rental_images',
            )
        )
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category_choices'] = Equipment.CATEGORY_CHOICES
        ctx['selected_category'] = self.request.GET.get('category', '')
        return ctx


class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = 'equipment/detail.html'
    context_object_name = 'equipment'

    def get_queryset(self):
        return Equipment.objects.filter(is_active=True).prefetch_related(
            Prefetch(
                'images',
                queryset=EquipmentImage.objects.filter(image_type='rental').order_by('order'),
                to_attr='rental_images',
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['rental_images'] = self.object.rental_images
        return ctx


class EquipmentCompareView(View):
    template_name = 'equipment/compare.html'

    def get(self, request):
        left_id = request.GET.get('left')
        right_id = request.GET.get('right')
        left = None
        right = None

        if left_id:
            try:
                left = Equipment.objects.get(pk=left_id, is_active=True)
            except Equipment.DoesNotExist:
                pass
        if right_id:
            try:
                right = Equipment.objects.get(pk=right_id, is_active=True)
            except Equipment.DoesNotExist:
                pass

        return render(request, self.template_name, {
            'category_choices': Equipment.CATEGORY_CHOICES,
            'left': left,
            'right': right,
        })


class EquipmentByCategoryAPI(View):
    def get(self, request):
        category = request.GET.get('category', '')
        qs = Equipment.objects.filter(is_active=True)
        if category:
            qs = qs.filter(category=category)
        data = []
        for e in qs:
            image_url = None
            if e.image:
                try:
                    image_url = e.image.url
                except Exception:
                    pass
            data.append({'id': e.id, 'name': e.name, 'image_url': image_url})
        return JsonResponse({'equipments': data})

from django.views.generic import ListView, DetailView
from django.db.models import Prefetch
from equipment.models import Equipment, EquipmentImage


class SalesListView(ListView):
    template_name = 'sales/list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        return Equipment.objects.filter(is_for_sale=True, is_active=True).prefetch_related(
            Prefetch(
                'images',
                queryset=EquipmentImage.objects.filter(image_type='sales').order_by('order'),
                to_attr='sales_images',
            )
        )


class SalesDetailView(DetailView):
    template_name = 'sales/detail.html'
    context_object_name = 'equipment'

    def get_queryset(self):
        return Equipment.objects.filter(is_for_sale=True, is_active=True).prefetch_related(
            Prefetch(
                'images',
                queryset=EquipmentImage.objects.filter(image_type='sales').order_by('order'),
                to_attr='sales_images',
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sales_images'] = self.object.sales_images
        return ctx

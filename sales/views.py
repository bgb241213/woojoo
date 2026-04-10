from django.views.generic import ListView, DetailView
from equipment.models import Equipment


class SalesListView(ListView):
    template_name = 'sales/list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        return Equipment.objects.filter(is_for_sale=True, is_active=True)


class SalesDetailView(DetailView):
    template_name = 'sales/detail.html'
    context_object_name = 'equipment'

    def get_queryset(self):
        return Equipment.objects.filter(is_for_sale=True, is_active=True)

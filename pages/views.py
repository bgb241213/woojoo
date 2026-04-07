from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from equipment.models import Equipment


class HomeView(View):
    template_name = 'pages/index.html'

    def get(self, request):
        featured = Equipment.objects.filter(is_active=True)[:4]
        return render(request, self.template_name, {'featured': featured})


class AboutView(TemplateView):
    template_name = 'pages/about.html'

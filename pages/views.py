from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render


class HomeView(View):
    template_name = 'pages/index.html'

    def get(self, request):
        return render(request, self.template_name, {
            'hero_images': ['images/hero/hero1.jpeg', 'images/hero/hero2.jpeg', 'images/hero/hero3.jpeg'],
        })


class AboutView(TemplateView):
    template_name = 'pages/about.html'

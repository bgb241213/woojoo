import json
import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from equipment.models import Equipment
from .models import QuoteRequest, QuoteItem


class QuoteCreateView(View):
    template_name = 'quotes/form.html'

    def get(self, request):
        return render(request, self.template_name, {
            'category_choices': Equipment.CATEGORY_CHOICES,
        })

    def post(self, request):
        errors = {}

        # Customer fields
        company_name     = request.POST.get('company_name', '').strip()
        name             = request.POST.get('name', '').strip()
        phone            = request.POST.get('phone', '').strip()
        email            = request.POST.get('email', '').strip()
        business_number  = request.POST.get('business_number', '').strip()
        start_date_str   = request.POST.get('start_date', '').strip()
        end_date_str     = request.POST.get('end_date', '').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        budget_str       = request.POST.get('budget', '').strip()
        message          = request.POST.get('message', '').strip()

        # Equipment items
        items_json = request.POST.get('items_json', '[]')
        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            items = []

        # Validation
        if not company_name:
            errors['company_name'] = '회사명을 입력해주세요.'
        if not name:
            errors['name'] = '담당자명을 입력해주세요.'
        if not phone:
            errors['phone'] = '연락처를 입력해주세요.'
        if not email:
            errors['email'] = '이메일을 입력해주세요.'
        if not delivery_address:
            errors['delivery_address'] = '배송지 주소를 입력해주세요.'

        # Date validation
        start_date = end_date = None
        today = datetime.date.today()
        if not start_date_str:
            errors['start_date'] = '렌탈 시작일을 입력해주세요.'
        else:
            try:
                start_date = datetime.date.fromisoformat(start_date_str)
                if start_date < today:
                    errors['start_date'] = '시작일은 오늘 이후여야 합니다.'
            except ValueError:
                errors['start_date'] = '올바른 날짜 형식이 아닙니다.'

        if not end_date_str:
            errors['end_date'] = '렌탈 종료일을 입력해주세요.'
        else:
            try:
                end_date = datetime.date.fromisoformat(end_date_str)
                if start_date and end_date < start_date:
                    errors['end_date'] = '종료일은 시작일 이후여야 합니다.'
            except ValueError:
                errors['end_date'] = '올바른 날짜 형식이 아닙니다.'

        if not items:
            errors['items'] = '장비를 1개 이상 선택해주세요.'

        if errors:
            return render(request, self.template_name, {
                'category_choices': Equipment.CATEGORY_CHOICES,
                'errors': errors,
                'post': request.POST,
            })

        # Save
        budget = int(budget_str) if budget_str.isdigit() else None
        quote = QuoteRequest.objects.create(
            company_name=company_name,
            name=name,
            phone=phone,
            email=email,
            business_number=business_number,
            start_date=start_date,
            end_date=end_date,
            delivery_address=delivery_address,
            budget=budget,
            message=message,
        )
        for item in items:
            try:
                equipment = Equipment.objects.get(pk=item['equipment_id'], is_active=True)
                QuoteItem.objects.create(
                    quote=quote,
                    equipment=equipment,
                    quantity=int(item['quantity']),
                )
            except (Equipment.DoesNotExist, KeyError, ValueError):
                pass

        return redirect('quotes:complete')


class QuoteCompleteView(TemplateView):
    template_name = 'quotes/complete.html'

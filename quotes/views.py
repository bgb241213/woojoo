import json
import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from equipment.models import Equipment
from .models import QuoteRequest, QuoteItem, CallbackRequest


class QuoteCreateView(View):
    template_name = 'quotes/form.html'

    # Height-class options offered on the quote form ("필요 작업고").
    # Mirrors the rental catalog's meter classes — keep in step with
    # Equipment.CATEGORY_CHOICES when the lineup changes.
    HEIGHT_CHOICES = ['미정', '1인승', '미니(6M급)', '7M', '10M', '12M', '14M', '기타장비']

    def _context(self, extra=None):
        ctx = {
            'inquiry_choices': QuoteRequest.INQUIRY_TYPE_CHOICES,
            'height_choices': self.HEIGHT_CHOICES,
        }
        if extra:
            ctx.update(extra)
        return ctx

    def get(self, request):
        return render(request, self.template_name, self._context())

    def post(self, request):
        errors = {}

        company_name     = request.POST.get('company_name', '').strip()
        name             = request.POST.get('name', '').strip()
        phone            = request.POST.get('phone', '').strip()
        email            = request.POST.get('email', '').strip()
        inquiry_type     = request.POST.get('inquiry_type', 'rental').strip()
        work_height      = request.POST.get('work_height_class', '').strip()
        start_date_str   = request.POST.get('start_date', '').strip()
        end_date_str     = request.POST.get('end_date', '').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        budget_str       = request.POST.get('budget', '').strip()
        message          = request.POST.get('message', '').strip()

        # Only the phone number is required; everything else is optional.
        if not phone:
            errors['phone'] = '연락처를 입력해주세요.'

        # Optional dates — accept blank, validate format when present.
        def parse_date(value, key):
            if not value:
                return None
            try:
                return datetime.date.fromisoformat(value)
            except ValueError:
                errors[key] = '올바른 날짜 형식이 아닙니다.'
                return None

        start_date = parse_date(start_date_str, 'start_date')
        end_date = parse_date(end_date_str, 'end_date')
        if start_date and end_date and end_date < start_date:
            errors['end_date'] = '종료일은 시작일 이후여야 합니다.'

        if inquiry_type not in dict(QuoteRequest.INQUIRY_TYPE_CHOICES):
            inquiry_type = 'rental'

        if errors:
            return render(request, self.template_name, self._context({
                'errors': errors,
                'post': request.POST,
            }))

        # Store a clean integer only when the budget is purely numeric;
        # anything with units/words (e.g. "500만원", "협의 가능") is preserved verbatim
        # in the message so no information is lost.
        budget = int(budget_str) if budget_str.isdigit() else None
        if budget_str and not budget_str.isdigit():
            message = (message + f'\n[예산] {budget_str}').strip()

        quote = QuoteRequest.objects.create(
            company_name=company_name,
            name=name,
            phone=phone,
            email=email,
            inquiry_type=inquiry_type,
            work_height_class=work_height,
            start_date=start_date,
            end_date=end_date,
            delivery_address=delivery_address,
            budget=budget,
            message=message,
        )

        # Optional equipment items (equipment pages may attach a selection).
        try:
            items = json.loads(request.POST.get('items_json', '[]'))
        except json.JSONDecodeError:
            items = []
        for item in items:
            try:
                equipment = Equipment.objects.get(pk=item['equipment_id'], is_active=True)
                QuoteItem.objects.create(quote=quote, equipment=equipment, quantity=int(item['quantity']))
            except (Equipment.DoesNotExist, KeyError, ValueError):
                pass

        return redirect('quotes:complete')


class QuoteCompleteView(TemplateView):
    template_name = 'quotes/complete.html'


@method_decorator(require_POST, name='dispatch')
class CallbackCreateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'}, status=400)

        phone = data.get('phone', '').strip()
        if not phone:
            return JsonResponse({'success': False, 'error': '전화번호를 입력해주세요.'}, status=400)

        CallbackRequest.objects.create(
            phone=phone,
            message=data.get('message', '').strip(),
        )
        return JsonResponse({'success': True})

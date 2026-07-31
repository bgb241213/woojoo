# 우주렌탈 홈페이지 프로젝트

## 프로젝트 개요
고소작업장비 렌탈 및 판매 전문 기업 **우주렌탈**의 공식 홈페이지.
B2B 고객(건설사, 시공업체 등)이 장비를 탐색하고 견적을 신청하면,
직원이 어드민 페이지에서 확인하고 연락하는 구조.

**핵심 목표**: 단순 견적 신청보다 **기업 브랜드 디스플레이**에 초점.
외부에서 보기에 세련되고 규모 있는 기업으로 보여야 함.

---

## 기술 스택
- **Backend**: Python 3.11+, Django 5.x
- **Frontend**: Bootstrap 5 (CDN) + 커스텀 CSS
- **JS 라이브러리**: Swiper.js, AOS.js, Particles.js, CountUp.js (모두 CDN)
- **폰트**: Noto Sans KR (Google Fonts CDN)
- **DB**: SQLite
- **어드민 UI**: django-jazzmin
- **이미지 저장**: Cloudflare R2 (django-storages, boto3)
- **정적 파일**: whitenoise
- **배포**: Railway (GitHub 연동 자동 배포)
- **환경변수**: python-dotenv (.env 파일)

---

## 디자인 시스템

### 컬러 팔레트
```css
--color-primary:  #1F286F;  /* 딥 네이비 — 헤더, 제목, 주요 버튼 */
--color-accent:   #E6503C;  /* 코랄 레드 — CTA 버튼, 배지, 강조 */
--color-bg:       #FFFFFF;  /* 흰색 — 기본 배경 */
--color-bg-sub:   #F5F6FA;  /* 연한 회색 — 섹션 구분 배경 */
--color-text:     #1A1A2E;  /* 다크 — 본문 텍스트 */
--color-text-sub: #6B7280;  /* 미디엄 그레이 — 설명 텍스트 */
--color-border:   #E5E7EB;  /* 연한 보더 */
```

포인트 컬러(#E6503C) 사용 원칙: CTA 버튼, 주요 배지, 호버 상태에만 제한적 사용.
전체 화면의 10% 이하로 유지.

### 타이포그래피
- 폰트: Noto Sans KR (Google Fonts CDN)
- 히어로 타이틀: 56~72px, Bold 700
- 섹션 제목: 36~44px, Bold 700
- 서브 제목: 24~28px, SemiBold 600
- 카드 제목: 18~20px, Medium 500
- 본문: 15~16px, Regular 400

### 공통 컴포넌트
- 카드: 배경 #FFFFFF, 테두리 1px solid #E5E7EB, 그림자 0 4px 20px rgba(31,40,111,0.08), border-radius 12px
- 카드 호버: translateY(-6px) + 그림자 강화 + 이미지 scale(1.05)
- 컨테이너 최대 너비: 1280px
- 섹션 상하 패딩: 80~120px

### 버튼
- Primary CTA: 배경 #E6503C, 텍스트 흰색 (견적신청, 주요 행동)
- Secondary: 배경 #1F286F, 텍스트 흰색 (상세보기)
- Outline: 투명 + #1F286F 테두리 (보조 액션)

---

## JavaScript 인터랙션

### CDN 목록 (base.html에 포함)
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"/>
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
<link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/countup.js/2.6.0/countUp.umd.min.js"></script>
```

### 인터랙션 명세
- 히어로 슬라이드쇼: Swiper.js, 5초 자동전환, fade 효과, 하단 도트
- 파티클: 흰색 점 80개, 마우스 반응, 히어로+견적 배너에 적용
- 카운트업: Intersection Observer 트리거, 3초 카운트
- 스크롤 애니메이션: AOS data-aos="fade-up", duration 600ms, 카드마다 100ms delay
- 네비게이션: 스크롤 전 투명+흰텍스트, 스크롤 100px 후 흰배경+네이비텍스트+그림자

---

## 프로젝트 구조
```
woojoo/
  config/
    settings.py / urls.py / wsgi.py
  equipment/               # 렌탈 장비
    models.py              # Equipment, EquipmentImage
    views.py / urls.py / admin.py
    templates/equipment/
      list.html / detail.html / compare.html
  sales/                   # 판매 장비
    views.py / urls.py
    templates/sales/
      list.html / detail.html
  quotes/                  # 견적
    models.py              # QuoteRequest, QuoteItem, CallbackRequest
    views.py / urls.py / admin.py / forms.py
    templates/quotes/
      form.html / complete.html
  pages/                   # 정적 페이지
    views.py / urls.py
    templates/pages/
      index.html / about.html
  templates/
    base.html
  static/
    css/main.css
    js/main.js
    images/
      logo.png
      hero/
        herotest1.jpg ~ herotest5.jpg
      장비카드썸네일용.jpg
```

---

## URL 구조
| URL | 설명 |
|-----|------|
| `/` | 메인 페이지 |
| `/about/` | 회사 소개 |
| `/equipment/` | 장비 렌탈 목록 |
| `/equipment/<id>/` | 장비 렌탈 상세 |
| `/equipment/compare/` | 장비 비교 |
| `/equipment/api/by-category/` | 카테고리별 장비 JSON |
| `/sales/` | 장비 판매 목록 |
| `/sales/<id>/` | 장비 판매 상세 |
| `/quote/` | 견적 신청 |
| `/quote/complete/` | 견적 완료 |
| `/quote/callback/` | 콜백 신청 (영업시간 외) |
| `/admin/` | 어드민 |

---

## 데이터 모델

### Equipment (장비 - 렌탈/판매 공통)
```python
name                = CharField(100)
category            = CharField(choices)   # 미터급
type                = CharField(choices)   # 타입
description         = TextField(blank=True)
max_work_height     = CharField(50)        # 작업가능높이
max_platform_height = CharField(50)        # 발판최대높이
equipment_weight    = CharField(50)        # 장비무게
max_load            = CharField(50)        # 적재가능중량
equipment_size      = CharField(100)       # 장비크기
platform_size       = CharField(100)       # 작업대크기
power_type          = CharField(50)        # 동력
is_active           = BooleanField(True)
is_for_sale         = BooleanField(False)  # 판매 가능 여부
created_at          = DateTimeField(auto)
```

### EquipmentImage (장비 다중 이미지) ← 신규
```python
equipment   = ForeignKey(Equipment, on_delete=CASCADE, related_name='images')
image       = ImageField(upload_to='equipment/')
image_type  = CharField(choices=[('rental','렌탈용'),('sales','판매용')])
order       = PositiveIntegerField(default=0)  # 이미지 순서
created_at  = DateTimeField(auto)

class Meta:
    ordering = ['order']
```
※ 렌탈 페이지와 판매 페이지에서 각각 다른 이미지 사용 가능
※ 어드민에서 인라인으로 여러 장 업로드

### QuoteRequest (견적 신청)
```python
company_name     = CharField(200)
name             = CharField(100)
phone            = CharField(20)
email            = EmailField
business_number  = CharField(20, blank=True)
start_date       = DateField
end_date         = DateField
delivery_address = TextField
budget           = PositiveIntegerField(null=True, blank=True)
message          = TextField(blank=True)
status           = CharField(choices)   # 대기/검토중/완료/취소
created_at       = DateTimeField(auto)
```

### QuoteItem (견적 장비 항목)
```python
quote     = ForeignKey(QuoteRequest, CASCADE)
equipment = ForeignKey(Equipment, PROTECT)
quantity  = PositiveIntegerField
```

### CallbackRequest (콜백 신청) ← 신규
```python
phone      = CharField(20)             # 고객 전화번호
message    = TextField(blank=True)     # 문의 내용 (선택)
is_called  = BooleanField(False)       # 전화 완료 여부
created_at = DateTimeField(auto)       # 신청 일시
```
※ 어드민에서 is_called로 완료 처리

---

## 장비 카테고리 및 타입
```python
CATEGORY_CHOICES = [
    ('5m', '5M급'), ('6m', '6M급'), ('7m', '7M급'), ('8m', '8M급'),
    ('10m', '10M급'), ('12m', '12M급'), ('14m', '14M급'),
]
TYPE_CHOICES = [
    ('scissor', '시저'), ('boom', '굴절'), ('vertical', '버티칼'), ('other', '기타'),
]
```

---

## 판매 장비 (5종)
Equipment 모델의 is_for_sale=True 필드로 구분.
판매 장비 모델명: JLG1230ES(1인승), SJ3219, JLG1932R, SJ3220, SJ4632

---

## 주요 기능 명세

### 1. 장비 다중 이미지 슬라이더
- 장비 목록 카드: 이미지 여러 장이면 Swiper 슬라이더로 넘길 수 있게
- 장비 상세 페이지: 메인 이미지 + 썸네일 갤러리
- 렌탈 페이지: image_type='rental' 이미지만 표시
- 판매 페이지: image_type='sales' 이미지만 표시
- 이미지 없으면 static/images/장비카드썸네일용.jpg 표시

### 2. 판매 사진 비율
- 판매 페이지(/sales/) 장비 카드 이미지: aspect-ratio 1:1 적용
- 렌탈 페이지는 기존 비율 유지

### 3. 구매문의 전화 연결 (영업시간 제한)
```
영업시간: 월–금 오전 8:00 ~ 오후 6:00 (토·일 휴무)

[구매 문의하기] 버튼 클릭 시:
  ↓
현재 시간 체크 (JavaScript)
  ↓
영업시간 내 (월–금 08:00~18:00):
  → 모달 표시: "대표에게 전화 연결합니다. 031-973-6661"
  → [확인] 클릭 시 tel:031-973-6661 로 바로 연결
  ↓
영업시간 외 (18:00~08:00, 토·일 종일):
  → 모달 표시: "영업시간(월–금 오전 8시~오후 6시)이 종료되었습니다.
               전화번호를 남겨주시면 다음 영업일에 연락드리겠습니다."
  → 전화번호 입력 폼 표시
  → 제출 시 CallbackRequest DB에 저장
  → 완료 메시지: "전화번호가 등록되었습니다. 내일 연락드리겠습니다."
```

### 4. 당근마켓 판매글 섹션
- 판매 상세 페이지(/sales/<id>/) 하단에 추가
- 해당 장비의 당근마켓 판매글 링크 버튼
- 당근마켓 로고 + "당근마켓에서도 구매 가능합니다" 문구
- 링크는 어드민에서 장비별로 입력 가능하도록
  (Equipment 모델에 daangn_url = URLField(blank=True) 추가)

### 5. AS/서비스/부품 강조
- 메인 페이지 서비스 특징 섹션에 AS/부품 카드 추가
- 판매 상세 페이지에 AS 안내 섹션 추가
- 회사 소개 페이지에 AS/서비스 섹션 강조

### 6. 회사 소개 페이지 리뉴얼
- 현재보다 더 풍성하고 신뢰감 있는 구성
- 구체적 방향은 별도 논의 필요

---

## 개발 예정 작업 목록 (우선순위 순)

### 즉시 작업 (간단)
- [ ] "500대" 문구 전체 삭제
- [ ] 판매 사진 1:1 비율 CSS 적용

### 단기 작업 (보통)
- [ ] 구매문의 전화 모달 + 영업시간 체크 JS
- [ ] CallbackRequest 모델 추가 + 어드민 등록
- [ ] 콜백 신청 뷰/템플릿 추가
- [ ] 당근마켓 URL 필드 Equipment 모델에 추가
- [ ] 판매 상세 하단 당근마켓 섹션
- [ ] AS/서비스/부품 강조 섹션

### 중기 작업 (복잡)
- [ ] EquipmentImage 모델 추가 + 마이그레이션
- [ ] 어드민 EquipmentImage 인라인 설정
- [ ] 장비 목록 카드 Swiper 슬라이더 적용
- [ ] 장비 상세 갤러리 적용
- [ ] 렌탈/판매 이미지 분리 로직
- [ ] 회사 소개 페이지 리뉴얼

---

## 배포 관련

### 배포 전 필수 작업 (장비 데이터 변경 시)
```bash
# 1. Railway 최신 데이터 덤프
railway run python manage.py dumpdata equipment.Equipment \
  --indent 2 --output equipment/fixtures/equipment_data.json

# 2. 커밋 후 push
git add equipment/fixtures/equipment_data.json
git commit -m "Update fixtures"
git push
```

### Procfile
```
web: python manage.py migrate && python manage.py loaddata equipment_data && python manage.py collectstatic --noinput && python manage.py ensure_admin && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

---

## 회사 정보
```
회사명: (주)우주렌탈 | 대표자: 박성조
주소: 경기도 고양시 덕양구 호국로1254번길 130-5(신원동)
전화: 031-973-6661 | 팩스: 02-381-3660
이메일: woojoo66666@daum.net
사업자번호: 326-88-01739
경력: 20년 이상
영업시간: 월–금 08:00 ~ 18:00 (토·일 휴무)
```

## 회사 소개글
```
안녕하십니까, 우주렌탈 홈페이지를 찾아주셔서 진심으로 감사드립니다.
우주렌탈은 고소작업대 렌탈의 전문 기업으로서, 다양한 현장에서 안전하고
효율적인 고소작업 환경을 제공하기 위해 노력하고 있습니다.
저희 우주렌탈은 철저한 장비 관리와 빠른 공급 서비스로 고객의 신뢰에
부응하기 위해 최선을 다하고 있습니다.
사용 중 문제가 생기면 지체 없이 현장으로 찾아가겠습니다.
우주렌탈 대표 박성조
```

---

## 네비게이션 메뉴
```
홈 | 회사소개 | 장비렌탈 | 장비판매 | 장비비교
```
우측에 [견적신청] 코랄 버튼 고정.

---

## 어드민
- django-jazzmin 사용
- Equipment: list_display(name,category,type,is_for_sale,is_active), fieldsets 그룹화
  EquipmentImage 인라인 추가 (image, image_type, order)
- QuoteRequest: list_display, list_filter, search_fields, QuoteItem 인라인
- CallbackRequest: list_display(phone,created_at,is_called), list_editable(is_called)

## 코딩 규칙
- 주석/변수명: 영어 | 사용자 텍스트: 한국어
- 뷰: 클래스 기반(CBV) 원칙
- 모델 변경 시 makemigrations → migrate 필수
- 새 기능: urls.py 연결까지 완료 후 보고

## 테스트 이미지 경로
```
히어로: static/images/hero/herotest1.jpg ~ herotest5.jpg
장비 기본 썸네일: static/images/장비카드썸네일용.jpg
```

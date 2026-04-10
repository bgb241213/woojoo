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
<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
<!-- Swiper.js -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"/>
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
<!-- AOS.js -->
<link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<!-- Particles.js -->
<script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
<!-- CountUp.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/countup.js/2.6.0/countUp.umd.min.js"></script>
```

### 인터랙션 명세
- 히어로 슬라이드쇼: Swiper.js, 5초 자동전환, fade 효과, 하단 도트
- 파티클: 흰색 점 80개, 마우스 반응, 히어로+견적 배너에 적용
- 카운트업: Intersection Observer 트리거, 2초 카운트 (500+대, 20+년)
- 스크롤 애니메이션: AOS data-aos="fade-up", duration 600ms, 카드마다 100ms delay
- 네비게이션: 스크롤 전 투명+흰텍스트, 스크롤 100px 후 흰배경+네이비텍스트+그림자

---

## 프로젝트 구조
```
woojoo/
  config/
    settings.py / urls.py / wsgi.py
  equipment/               # 렌탈 장비
    models.py / views.py / urls.py / admin.py
    templates/equipment/
      list.html / detail.html / compare.html
  sales/                   # 판매 장비 (신규)
    views.py / urls.py
    templates/sales/
      list.html / detail.html
  quotes/                  # 견적
    models.py / views.py / urls.py / admin.py / forms.py
    templates/quotes/
      form.html / complete.html
  pages/                   # 정적 페이지
    views.py / urls.py
    templates/pages/
      index.html / about.html
  templates/
    base.html
  static/
    css/main.css           # CSS 변수 및 커스텀 스타일
    js/main.js             # 공통 JS
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
| `/sales/` | 장비 판매 목록 (신규) |
| `/sales/<id>/` | 장비 판매 상세 (신규) |
| `/quote/` | 견적 신청 |
| `/quote/complete/` | 견적 완료 |
| `/admin/` | 어드민 |

---

## 판매 장비 (5종)
Equipment 모델의 is_for_sale=True 필드로 구분.
판매 장비 모델명: JLG1230ES(1인승), SJ3219, JLG1932R, SJ3220, SJ4632

---

## 데이터 모델

### Equipment
```python
name                = CharField(100)
category            = CharField(choices)   # 미터급
type                = CharField(choices)   # 타입
image               = ImageField
description         = TextField(blank=True)
max_work_height     = CharField(50)        # 작업가능높이
max_platform_height = CharField(50)        # 발판최대높이
equipment_weight    = CharField(50)        # 장비무게
max_load            = CharField(50)        # 적재가능중량
equipment_size      = CharField(100)       # 장비크기
platform_size       = CharField(100)       # 작업대크기
power_type          = CharField(50)        # 동력
is_active           = BooleanField(True)
is_for_sale         = BooleanField(False)  # 판매 가능 여부 (신규 필드)
created_at          = DateTimeField(auto)
```

### QuoteRequest
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

### QuoteItem
```python
quote     = ForeignKey(QuoteRequest, CASCADE)
equipment = ForeignKey(Equipment, PROTECT)
quantity  = PositiveIntegerField
```

---

## 장비 카테고리 및 타입
```python
CATEGORY_CHOICES = [
    ('5m', '5M급'), ('6m', '6M급'), ('7m', '7M급'), ('8m', '8M급'),
    ('10m', '10M급'), ('12m', '12M급'), ('14m', '14M급'), ('15m_boom', '15M급 굴절형'),
]
TYPE_CHOICES = [
    ('scissor', '시저'), ('boom', '굴절'), ('vertical', '버티칼'), ('other', '기타'),
]
```

---

## 장비 데이터 (29개)
형식: (모델명, 카테고리, 타입, 동력, 작업가능높이, 발판최대높이, 장비무게, 적재가능중량, 장비크기, 작업대크기, is_for_sale)
```
JLG1230ES       5m       vertical  배터리  5.7m   3.66m  800kg    227kg  1.36x0.76x1.66m  0.84x0.68m   True(판매)
LGMG SS0407     6m       scissor   배터리  5.6m   3.6m   880kg    240kg  1.35x0.76x1.8m   1.35x0.7m    False
JCPT0607DCS     6m       scissor   배터리  5.6m   3.6m   880kg    240kg  1.44x0.76x1.8m   1.29x0.7m    False
JLG ES1530L     6m       scissor   배터리  6.4m   4.5m   880kg    227kg  1.33x0.76x1.8m   1.3x0.6m     False
SJ3215          6m       scissor   배터리  6.4m   4.57m  1120kg   227kg  1.78x0.81x1.88m  1.63x0.66m   False
SJ3219          7m       scissor   배터리  7.62m  5.79m  1312kg   227kg  1.78x0.81x1.99m  1.63x0.66m   True(판매)
JLG ES1932      7m       scissor   배터리  7.6m   5.8m   1565kg   230kg  1.7x0.81x2.1m    1.59x0.64m   False
JLG1932R        7m       scissor   배터리  7.8m   5.8m   1193kg   250kg  1.74x0.81x1.99m  1.59x0.64m   True(판매)
JLG1930ES       7m       scissor   배터리  7.72m  5.72m  1229kg   227kg  1.87x0.76x2.02m  1.87x0.76m   False
JCPT0807AC      7m       scissor   배터리  7.8m   5.8m   1630kg   230kg  1.86x0.76x2.15m  1.67x0.74m   False
LGMG AS0607E    7m       scissor   배터리  7.8m   5.8m   1420kg   230kg  1.86x0.76x2.14m  1.63x0.74m   False
SJ3220          8m       scissor   배터리  7.92m  6.1m   1592kg   408kg  2.32x0.81x1.97m  2.13x0.71m   True(판매)
JLG2032ES       8m       scissor   배터리  7.92m  6.1m   1638kg   363kg  2.3x0.81x2.2m    2.3x0.76m    False
SJ3226          10m      scissor   배터리  9.8m   7.92m  1876kg   227kg  2.32x0.81x2.15m  2.13x0.71m   False
JLG2632ES       10m      scissor   배터리  9.6m   7.8m   2103kg   227kg  2.3x0.81x2.33m   2.3x0.76m    False
JCPT1008AC      10m      scissor   배터리  10m    8m     2230kg   230kg  2.48x0.83x2.36m  2.27x0.81m   False
SJ4626          10m      scissor   배터리  9.8m   7.92m  2132kg   454kg  2.31x1.17x2.15m  2.13x1.07m   False
LGMG AS0812     10m      scissor   배터리  10m    8m     2430kg   450kg  2.42x1.18x2.3m   2.26x1.12m   False
JCPT1012AC      10m      scissor   배터리  10m    8m     2710kg   450kg  2.48x1.15x2.36m  2.27x1.12m   False
JLG ES3246      12m      scissor   배터리  11.6m  9.7m   2257kg   318kg  2.4x1.17x2.22m   2.5x1.12m    False
JLG3246ES       12m      scissor   배터리  11.68m 9.68m  2279kg   454kg  2.5x1.17x2.36m   2.5x1.12m    False
SJ4632          12m      scissor   배터리  11.6m  9.8m   2302kg   318kg  2.32x1.17x2.22m  2.13x1.07m   True(판매)
LGMG AS1012     12m      scissor   배터리  12m    10m    3000kg   320kg  2.47x1.18x2.43m  2.26x1.12m   False
JCPT1212AC      12m      scissor   배터리  12m    10m    3060kg   320kg  2.48x1.15x2.49m  2.27x1.12m   False
LGMG AS1212     14m      scissor   배터리  14m    12m    3160kg   320kg  2.47x1.18x2.56m  2.26x1.12m   False
JCPT1412AC      14m      scissor   배터리  13.8m  11.8m  2990kg   320kg  2.48x1.19x2.62m  2.27x1.12m   False
XE140W          14m      scissor   배터리  14m    12m    3245kg   350kg  2.42x1.2x2.51m   2.3x1.15m    False
JLG4069LE       14m      scissor   배터리  14.2m  12.2m  5216kg   360kg  3.15x1.75x2.83m  2.92x1.65m   False
Z45             15m_boom boom      디젤    15.86m 13.86m 6515kg   227kg  6.65x2.29x2.13m  0.76x1.83m   False
```

---

## 회사 정보
```
회사명: 우주렌탈 | 대표자: 박성조
주소: 경기도 고양시 덕양구 호국로1254번길 130-5(신원동)
전화: 031-973-6661 | 팩스: 02-381-3660 | 이메일: woojoo66666@daum.net
사업자번호: 326-88-01739 | 보유장비: 500여대 | 경력: 20년 이상
```

## 회사 소개글
```
안녕하십니까, 우주렌탈 홈페이지를 찾아주셔서 진심으로 감사드립니다.
우주렌탈은 고소작업대 렌탈의 전문 기업으로서, 다양한 현장에서 안전하고
효율적인 고소작업 환경을 제공하기 위해 노력하고 있습니다.
저희 우주렌탈은 철저한 장비 관리와 빠른 공급 서비스로 고객의 신뢰에
부응하기 위해 최선을 다하고 있습니다.
우주렌탈과 함께라면 언제나 안전하고 효율적인 작업 환경을 경험하실 수 있음을 약속드립니다.
우주렌탈 대표 박성조
```

---

## 배포 설정
- 플랫폼: Railway | DB: SQLite | 이미지: Cloudflare R2 | 정적파일: whitenoise
- Procfile: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT

## 어드민
- django-jazzmin 사용
- Equipment: list_display(name,category,type,is_for_sale,is_active), fieldsets 그룹화
- QuoteRequest: list_display, list_filter, search_fields, QuoteItem 인라인

## 코딩 규칙
- 주석/변수명: 영어 | 사용자 텍스트: 한국어
- 뷰: 클래스 기반(CBV) 원칙
- 모델 변경 시 makemigrations → migrate 필수
- 새 기능: urls.py 연결까지 완료 후 보고

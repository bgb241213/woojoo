# 우주렌탈 홈페이지 프로젝트

## 프로젝트 개요
고소작업장비 렌탈 전문 기업 **우주렌탈**의 공식 홈페이지.
B2B 고객(건설사, 시공업체 등)이 장비를 탐색하고 견적을 신청하면,
직원이 어드민 페이지에서 확인하고 연락하는 구조.

---

## 기술 스택
- **Backend**: Python 3.11+, Django 5.x
- **Frontend**: Bootstrap 5 (CDN)
- **DB**: SQLite
- **어드민 UI**: django-jazzmin
- **이미지 저장**: Cloudflare R2 (django-storages, boto3)
- **정적 파일**: whitenoise
- **배포**: Railway (GitHub 연동 자동 배포)
- **환경변수**: python-dotenv (.env 파일)

---

## 프로젝트 구조
```
woojoo/
  config/                  # Django 프로젝트 설정
    settings.py
    urls.py
    wsgi.py
  equipment/               # 장비 앱
    models.py
    views.py
    urls.py
    admin.py
    templates/equipment/
      list.html
      detail.html
      compare.html
  quotes/                  # 견적 앱
    models.py
    views.py
    urls.py
    admin.py
    forms.py
    templates/quotes/
      form.html
      complete.html
  pages/                   # 정적 페이지 앱
    views.py
    urls.py
    templates/pages/
      index.html
      about.html
  templates/
    base.html              # 공통 레이아웃
  static/
    images/
      logo.png             # 우주렌탈 로고
    css/
    js/
  media/                   # 장비 이미지 업로드 (로컬 개발용)
  requirements.txt
  .env
  .gitignore
  Procfile
  railway.toml
  CLAUDE.md
```

---

## URL 구조
| URL | 앱 | 설명 |
|-----|----|------|
| `/` | pages | 메인 페이지 |
| `/about/` | pages | 회사 소개 |
| `/equipment/` | equipment | 장비 목록 (미터급 탭 필터) |
| `/equipment/<id>/` | equipment | 장비 상세 |
| `/equipment/compare/` | equipment | 장비 비교 (2개) |
| `/equipment/api/by-category/` | equipment | 카테고리별 장비 JSON API |
| `/quote/` | quotes | 견적 신청 폼 |
| `/quote/complete/` | quotes | 견적 완료 |
| `/admin/` | - | django-jazzmin 어드민 |

---

## 데이터 모델

### Equipment (장비)
```python
name           = CharField(100)        # 모델명 (예: SJ3219)
category       = CharField(choices)    # 미터급 (아래 카테고리 참고)
type           = CharField(choices)    # 타입 (시저/굴절/버티칼/기타)
image          = ImageField            # 장비 사진 (Cloudflare R2)
description    = TextField(blank=True) # 장비 설명
# 스펙 8개 항목 (CharField - 단위 포함 자유 텍스트)
max_work_height   = CharField(50)      # 작업가능높이 (예: 7.62m)
max_platform_height = CharField(50)   # 발판최대높이 (예: 5.79m)
equipment_weight  = CharField(50)     # 장비무게 (예: 1,312kg)
max_load          = CharField(50)     # 적재가능중량 (예: 227kg)
equipment_size    = CharField(100)    # 장비크기 (예: 1.78 x 0.81 x 1.99m)
platform_size     = CharField(100)    # 작업대크기 (예: 1.63 x 0.66m)
power_type        = CharField(50)     # 동력 (예: 배터리, 디젤)
is_active      = BooleanField(True)   # 노출 여부
created_at     = DateTimeField(auto)
```

### QuoteRequest (견적 신청)
```python
company_name     = CharField(200)      # 회사명
name             = CharField(100)      # 담당자명
phone            = CharField(20)       # 연락처
email            = EmailField          # 이메일
business_number  = CharField(20, blank=True)  # 사업자번호 (선택)
start_date       = DateField           # 렌탈 시작일
end_date         = DateField           # 렌탈 종료일
delivery_address = TextField           # 배송지 주소
budget           = PositiveIntegerField(null=True, blank=True)  # 예산
message          = TextField(blank=True)  # 추가 요청사항
status           = CharField(choices)  # 대기/검토중/완료/취소 (default: 대기)
created_at       = DateTimeField(auto)
```

### QuoteItem (견적 장비 항목)
```python
quote      = ForeignKey(QuoteRequest, on_delete=CASCADE)
equipment  = ForeignKey(Equipment, on_delete=PROTECT)
quantity   = PositiveIntegerField      # 수량
```

---

## 장비 카테고리
```python
CATEGORY_CHOICES = [
    ('5m',    '5M급'),
    ('6m',    '6M급'),
    ('7m',    '7M급'),
    ('8m',    '8M급'),
    ('10m',   '10M급'),
    ('12m',   '12M급'),
    ('14m',   '14M급'),
    ('15m_boom', '15M급 굴절형'),
]
```
※ 6M급(mini)는 6M급에 포함

## 장비 타입
```python
TYPE_CHOICES = [
    ('scissor',  '시저'),
    ('boom',     '굴절'),
    ('vertical', '버티칼'),
    ('other',    '기타'),
]
```

---

## 실제 장비 데이터 (29개)
아래 데이터를 fixtures로 만들어 사용한다.
형식: (모델명, 카테고리, 타입, 동력, 작업가능높이, 발판최대높이, 장비무게, 적재가능중량, 장비크기, 작업대크기)

```
('JLG1230ES',       '5m',      'vertical', '배터리', '5.7m',   '3.66m', '800kg',   '227kg', '1.36 x 0.76 x 1.66m', '0.84 x 0.68m')
('LGMG SS0407',     '6m',      'scissor',  '배터리', '5.6m',   '3.6m',  '880kg',   '240kg', '1.35 x 0.76 x 1.8m',  '1.35 x 0.7m')
('JCPT0607DCS',     '6m',      'scissor',  '배터리', '5.6m',   '3.6m',  '880kg',   '240kg', '1.44 x 0.76 x 1.8m',  '1.29 x 0.7m')
('JLG ES1530L',     '6m',      'scissor',  '배터리', '6.4m',   '4.5m',  '880kg',   '227kg', '1.33 x 0.76 x 1.8m',  '1.3 x 0.6m')
('SJ3215',          '6m',      'scissor',  '배터리', '6.4m',   '4.57m', '1,120kg', '227kg', '1.78 x 0.81 x 1.88m', '1.63 x 0.66m')
('SJ3219',          '7m',      'scissor',  '배터리', '7.62m',  '5.79m', '1,312kg', '227kg', '1.78 x 0.81 x 1.99m', '1.63 x 0.66m')
('JLG ES1932',      '7m',      'scissor',  '배터리', '7.6m',   '5.8m',  '1,565kg', '230kg', '1.7 x 0.81 x 2.1m',   '1.59 x 0.64m')
('JLG1932R',        '7m',      'scissor',  '배터리', '7.8m',   '5.8m',  '1,193kg', '250kg', '1.74 x 0.81 x 1.99m', '1.59 x 0.64m')
('JLG1930ES',       '7m',      'scissor',  '배터리', '7.72m',  '5.72m', '1,229kg', '227kg', '1.87 x 0.76 x 2.02m', '1.87 x 0.76m')
('JCPT0807AC',      '7m',      'scissor',  '배터리', '7.8m',   '5.8m',  '1,630kg', '230kg', '1.86 x 0.76 x 2.15m', '1.67 x 0.74m')
('LGMG AS0607E',    '7m',      'scissor',  '배터리', '7.8m',   '5.8m',  '1,420kg', '230kg', '1.86 x 0.76 x 2.14m', '1.63 x 0.74m')
('SJ3220',          '8m',      'scissor',  '배터리', '7.92m',  '6.1m',  '1,592kg', '408kg', '2.32 x 0.81 x 1.97m', '2.13 x 0.71m')
('JLG2032ES',       '8m',      'scissor',  '배터리', '7.92m',  '6.1m',  '1,638kg', '363kg', '2.3 x 0.81 x 2.2m',   '2.3 x 0.76m')
('SJ3226',          '10m',     'scissor',  '배터리', '9.8m',   '7.92m', '1,876kg', '227kg', '2.32 x 0.81 x 2.15m', '2.13 x 0.71m')
('JLG2632ES',       '10m',     'scissor',  '배터리', '9.6m',   '7.8m',  '2,103kg', '227kg', '2.3 x 0.81 x 2.33m',  '2.3 x 0.76m')
('JCPT1008AC',      '10m',     'scissor',  '배터리', '10m',    '8m',    '2,230kg', '230kg', '2.48 x 0.83 x 2.36m', '2.27 x 0.81m')
('SJ4626',          '10m',     'scissor',  '배터리', '9.8m',   '7.92m', '2,132kg', '454kg', '2.31 x 1.17 x 2.15m', '2.13 x 1.07m')
('LGMG AS0812',     '10m',     'scissor',  '배터리', '10m',    '8m',    '2,430kg', '450kg', '2.42 x 1.18 x 2.3m',  '2.26 x 1.12m')
('JCPT1012AC',      '10m',     'scissor',  '배터리', '10m',    '8m',    '2,710kg', '450kg', '2.48 x 1.15 x 2.36m', '2.27 x 1.12m')
('JLG ES3246',      '12m',     'scissor',  '배터리', '11.6m',  '9.7m',  '2,257kg', '318kg', '2.4 x 1.17 x 2.22m',  '2.5 x 1.12m')
('JLG3246ES',       '12m',     'scissor',  '배터리', '11.68m', '9.68m', '2,279kg', '454kg', '2.5 x 1.17 x 2.36m',  '2.5 x 1.12m')
('SJ4632',          '12m',     'scissor',  '배터리', '11.6m',  '9.8m',  '2,302kg', '318kg', '2.32 x 1.17 x 2.22m', '2.13 x 1.07m')
('LGMG AS1012',     '12m',     'scissor',  '배터리', '12m',    '10m',   '3,000kg', '320kg', '2.47 x 1.18 x 2.43m', '2.26 x 1.12m')
('JCPT1212AC',      '12m',     'scissor',  '배터리', '12m',    '10m',   '3,060kg', '320kg', '2.48 x 1.15 x 2.49m', '2.27 x 1.12m')
('LGMG AS1212',     '14m',     'scissor',  '배터리', '14m',    '12m',   '3,160kg', '320kg', '2.47 x 1.18 x 2.56m', '2.26 x 1.12m')
('JCPT1412AC',      '14m',     'scissor',  '배터리', '13.8m',  '11.8m', '2,990kg', '320kg', '2.48 x 1.19 x 2.62m', '2.27 x 1.12m')
('XE140W',          '14m',     'scissor',  '배터리', '14m',    '12m',   '3,245kg', '350kg', '2.42 x 1.2 x 2.51m',  '2.3 x 1.15m')
('JLG4069LE',       '14m',     'scissor',  '배터리', '14.2m',  '12.2m', '5,216kg', '360kg', '3.15 x 1.75 x 2.83m', '2.92 x 1.65m')
('Z45',             '15m_boom','boom',     '디젤',   '15.86m', '13.86m','6,515kg', '227kg', '6.65 x 2.29 x 2.13m', '0.76 x 1.83m')
```

---

## 회사 정보 (about 페이지, 푸터에 사용)
```
회사명:       우주렌탈
대표자:       박성조
주소:         경기도 고양시 덕양구 호국로1254번길 130-5(신원동)
전화:         010-5443-2848
이메일:       woojoo66666@daum.net
사업자번호:   326-88-01739
보유 장비:    500여대
경력:         20년 이상
강점:         빠른 납품, 20년 이상 전문 렌탈사, 500여대 보유
```

## 회사 소개글 (about 페이지 본문)
```
안녕하십니까,
우주렌탈 홈페이지를 찾아주셔서 진심으로 감사드립니다.

우주렌탈은 고소작업대 렌탈의 전문 기업으로서, 다양한 현장에서 안전하고 효율적인
고소작업 환경을 제공하기 위해 노력하고 있습니다.
고소작업대는 작업자의 안전을 보장하면서도 생산성을 높일 수 있는 필수 장비입니다.
저희는 이러한 장비를 필요한 순간에 신속하고 안전하게 공급하여
고객 여러분의 성공적인 프로젝트에 기여하는 것을 목표로 하고 있습니다.

저희 우주렌탈은 철저한 장비 관리와 빠른 공급 서비스로 고객의 신뢰에 부응하기 위해
최선을 다하고 있으며, 고객 만족을 최우선으로 하는 서비스를 제공하겠습니다.
앞으로도 많은 관심과 성원을 부탁드리며,
우주렌탈과 함께라면 언제나 안전하고 효율적인 작업 환경을 경험하실 수 있음을 약속드립니다.

감사합니다.
우주렌탈 대표 박성조
```

---

## 디자인 가이드
- **메인 컬러**: 네이비 (#1E3A5F)
- **포인트 컬러**: 흰색, 밝은 회색
- **폰트**: 시스템 기본 (sans-serif)
- **UI 프레임워크**: Bootstrap 5 (CDN)
- **로고**: static/images/logo.png (투명 배경 PNG)
- **톤앤매너**: 신뢰감 있고 전문적, B2B 타겟

---

## 어드민 설정 (django-jazzmin)
- 비개발자 직원도 혼자 쓸 수 있도록 UI 최대한 직관적으로
- Equipment 어드민:
  - list_display: name, category, type, is_active, created_at
  - list_filter: category, type, is_active
  - list_editable: is_active
  - fieldsets으로 그룹화: [기본정보] [스펙정보] [설정]
- QuoteRequest 어드민:
  - list_display: company_name, name, phone, status, created_at
  - list_filter: status, created_at
  - search_fields: company_name, name, phone
  - QuoteItem 인라인으로 신청 장비 목록 표시

---

## 견적 신청 UX (quotes 앱)
- 다중 장비 선택 (페이지 내 추가형)
- 미터급 드롭다운 선택 → 해당 장비 목록 동적 표시 (JavaScript + /equipment/api/by-category/ API)
- 장비 선택 + 수량 입력 → [장비 추가] 버튼으로 반복
- 선택된 장비 목록 카드 형태 표시 (삭제 가능)
- 고객 정보 입력: 회사명(필수), 담당자명(필수), 연락처(필수), 이메일(필수), 사업자번호(선택), 시작일(필수), 종료일(필수), 배송지(필수), 예산(선택), 추가요청사항(선택)
- 날짜 validation: 시작일은 오늘 이후, 종료일은 시작일 이후

## 장비 비교 UX (equipment/compare/)
- 2개 장비를 나란히 비교
- 왼쪽/오른쪽 각각: 미터급 드롭다운 → 장비 드롭다운 (연동)
- [비교하기] 버튼 → 하단에 스펙 비교 테이블
- 비교 항목 순서: 장비이미지, 장비명, 타입, 작업가능높이, 발판최대높이, 작업대크기, 장비크기, 장비무게, 적재가능중량, 동력
- 각 장비 하단 [견적신청] 버튼

---

## 배포 설정
- **플랫폼**: Railway
- **DB**: SQLite (파일 기반, 별도 서버 불필요)
- **이미지**: Cloudflare R2
- **정적파일**: whitenoise

### 환경변수 (.env)
```
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_ENDPOINT_URL=
```

### Procfile
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

---

## 코딩 규칙
- 모든 주석과 변수명은 영어로
- 템플릿 내 사용자에게 보이는 텍스트는 한국어
- 뷰는 클래스 기반 뷰(CBV) 사용 원칙 (단순한 경우 함수 기반 뷰도 허용)
- 모델 변경 시 반드시 makemigrations → migrate 실행
- 새 기능 추가 시 urls.py 연결까지 완료 후 완료 보고
- 로컬 개발 시 이미지는 media/ 폴더에 저장 (Cloudflare R2는 배포 시 전환)

# 우주렌탈 홈페이지

고소작업장비 렌탈 전문 기업 **우주렌탈**의 공식 홈페이지입니다.

## 기술 스택

- **Backend**: Python 3.11+, Django 5.x
- **Frontend**: Bootstrap 5 (CDN)
- **DB**: SQLite
- **어드민 UI**: django-jazzmin
- **이미지 저장**: Cloudflare R2 (운영) / media/ 폴더 (로컬)
- **정적 파일**: whitenoise
- **배포**: Railway

---

## 로컬 개발 환경 설정

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. .env 파일 생성 (아래 환경변수 섹션 참고)

# 4. DB 마이그레이션
python manage.py migrate

# 5. 장비 데이터 로드
python manage.py loaddata equipment_data

# 6. 관리자 계정 생성
python manage.py createsuperuser

# 7. 서버 실행
python manage.py runserver
```

---

## 환경변수 (.env)

프로젝트 루트에 `.env` 파일을 생성하고 아래 항목을 설정합니다.

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Cloudflare R2 (운영 환경에서만 필요)
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_ENDPOINT_URL=
```

---

## Cloudflare R2 이미지 저장소 설정

운영 환경(`DEBUG=False`)에서는 장비 이미지가 Cloudflare R2에 저장됩니다.
아래 순서로 설정하세요.

### 1. R2 버킷 생성

1. [Cloudflare 대시보드](https://dash.cloudflare.com) 로그인
2. 좌측 메뉴 **R2 Object Storage** 클릭
3. **Create bucket** → 버킷 이름 입력 (예: `woojoo-media`)
4. 리전은 기본값 유지 후 생성

### 2. 버킷 Public Access 활성화 (필수)

이미지를 웹에서 공개적으로 볼 수 있으려면 Public Access를 반드시 활성화해야 합니다.

1. 생성한 버킷 클릭 → **Settings** 탭
2. **Public Access** 섹션 → **Allow Access** 클릭
3. 활성화하면 `https://<bucket-name>.<account-id>.r2.cloudflarestorage.com` 형태의 퍼블릭 URL이 생성됩니다.

> **커스텀 도메인 사용 (권장)**
> Settings → Custom Domains에서 도메인을 연결하면
> `https://media.yourdomain.com/...` 형태로 이미지를 서빙할 수 있습니다.

### 3. API 토큰 발급

1. Cloudflare 대시보드 우측 상단 프로필 → **My Profile**
2. **API Tokens** → **Create Token**
3. **Edit Cloudflare Workers** 템플릿 사용 또는 아래 권한 직접 설정:
   - **Account** → R2 Storage → Edit
4. 발급된 **Access Key ID**와 **Secret Access Key** 저장

### 4. 엔드포인트 URL 확인

1. R2 대시보드 → **Overview**
2. **Account ID** 확인
3. 엔드포인트 URL 형식:
   ```
   https://<ACCOUNT_ID>.r2.cloudflarestorage.com
   ```

### 5. Railway 환경변수 설정

Railway 대시보드 → 프로젝트 → **Variables** 탭에서 아래 항목 추가:

| 변수명 | 값 |
|--------|-----|
| `SECRET_KEY` | 랜덤 비밀키 (필수) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app.railway.app` |
| `R2_ACCESS_KEY_ID` | Cloudflare API Access Key ID |
| `R2_SECRET_ACCESS_KEY` | Cloudflare API Secret Access Key |
| `R2_BUCKET_NAME` | 버킷 이름 (예: `woojoo-media`) |
| `R2_ENDPOINT_URL` | `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` |

---

## 어드민 접속

- URL: `/admin/`
- 로컬 기본 계정: `admin` / `admin1234`

---

## 배포 (Railway)

GitHub 레포지토리와 Railway를 연동하면 `main` 브랜치 push 시 자동 배포됩니다.
배포 시 아래 명령이 자동 실행됩니다:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

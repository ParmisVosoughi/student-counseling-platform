# سامانه مدیریت مشاوره تحصیلی

یک سامانه Full-Stack برای مدیریت ساختار **مدیر → ناظر → مشاور → دانش‌آموز**، ثبت عملکرد هفتگی، نگهداری نتایج ارزیابی‌های روان‌شناختی انجام‌شده خارج از سامانه، ثبت چالش‌ها، بررسی منطق برنامه توسط ناظر، پیگیری اجرای راهکار و گزارش‌های مدیریتی داده‌محور.

> این سامانه **آزمون روان‌شناختی اجرا نمی‌کند**، سؤال یا موتور نمره‌دهی ندارد و تشخیص/تفسیر روان‌شناختی خودکار ارائه نمی‌دهد. فقط نتایج بیرونی را که مشاور وارد می‌کند ذخیره و نمایش می‌دهد.


## اجرای فوق‌ساده در ویندوز

این نسخه برای اجرای محلی بدون تنظیم دستی آماده شده است. اگر Docker Desktop نصب و روشن است:

1. روی `START.bat` دوبار کلیک کنید.
2. اسکریپت به‌صورت خودکار یک پورت آزاد از 18088 به بعد پیدا می‌کند.
3. migrationها و داده اولیه در اولین اجرا خودکار ساخته می‌شوند.
4. مرورگر به‌صورت خودکار باز می‌شود.

برای توقف، `STOP.bat` را اجرا کنید. برای پاک‌کردن کامل داده‌های محلی، `RESET-ALL-DATA.bat` را اجرا کنید.

در این حالت نیازی به ساخت `.env` یا آزاد بودن پورت 8000 نیست.

## معماری و فناوری‌ها

- Backend: Python, Django, Django REST Framework
- Authentication: JWT access token + HttpOnly refresh cookie
- Database: PostgreSQL
- API documentation: OpenAPI / Swagger via drf-spectacular
- Frontend: React, Vite, TypeScript, Tailwind CSS, React Router, Axios, Recharts
- UI: فارسی، RTL، responsive از موبایل تا دسکتاپ
- Infrastructure: Docker Compose، PostgreSQL، Gunicorn + WhiteNoise، Nginx

## ساختار پروژه

```text
student-counseling-platform/
├── backend/
│   ├── accounts/
│   ├── counseling/
│   ├── dashboard/
│   ├── config/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── manage.py
│   ├── pytest.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── scripts/verify.sh
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## قابلیت‌های اصلی

### مدیر

- مشاهده و مدیریت همه کاربران
- ایجاد ناظر و مشاور
- تخصیص/تغییر ناظر مشاور
- فعال/غیرفعال‌سازی حساب‌ها
- تغییر رمز عبور بدون امکان مشاهده رمز قبلی
- مشاهده همه دانش‌آموزان، چالش‌ها، ارزیابی‌ها و بررسی‌های ناظر
- داشبورد آماری کل سامانه

### ناظر

- مشاهده فقط مشاوران زیرمجموعه خود
- ایجاد و ویرایش حساب مشاوران زیرمجموعه
- غیرفعال‌سازی مشاور زیرمجموعه
- مشاهده دانش‌آموزان تیم
- مشاهده عملکرد هفتگی، نتایج ارزیابی و چالش‌ها
- ثبت بررسی منطق برنامه
- ثبت شدت ایراد، محل ایراد، چند دسته ایراد و راهکار اصلاحی
- پیگیری وضعیت اجرای راهکارها
- داشبورد شامل دانش‌آموزان نیازمند توجه و خلاصه عملکرد مشاوران

### مشاور

- ایجاد، ویرایش و بایگانی دانش‌آموز
- ثبت/ویرایش عملکرد هفتگی
- ثبت/ویرایش نتیجه ارزیابی بیرونی با پارامترهای داینامیک
- ثبت و به‌روزرسانی چالش‌ها
- مشاهده نمودار پیشرفت
- مشاهده بازخورد ناظر
- ثبت وضعیت اجرای راهکار و توضیح اجرا

## الزامات نصب با Docker

- Docker Engine / Docker Desktop
- Docker Compose v2

### 1) تنظیم محیط

```bash
cp .env.example .env
```

مقادیر حداقل زیر را در `.env` تغییر دهید:

```env
DJANGO_SECRET_KEY=your-long-random-secret
POSTGRES_PASSWORD=your-strong-db-password
```

برای اجرای محلی پیش‌فرض، این مقادیر مناسب هستند:

```env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000/api
COOKIE_SECURE=False
```

### 2) اجرای کل سامانه

```bash
docker compose up --build
```

Container بک‌اند در startup، migrationها را اجرا و static files را جمع‌آوری می‌کند.

### 3) آدرس‌ها

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/`
- Swagger: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`
- Django Admin: `http://localhost:8000/admin/`

## ایجاد مدیر اصلی

در یک ترمینال دیگر:

```bash
docker compose exec backend python manage.py createsuperuser
```

کاربری که با `createsuperuser` ساخته می‌شود به‌صورت خودکار role برابر `ADMIN` می‌گیرد.

## Seed Data توسعه

```bash
docker compose exec backend python manage.py seed_demo
```

این فرمان داده کافی برای بررسی workflowها ایجاد می‌کند: ناظر، مشاور، دانش‌آموز، چند هفته عملکرد، ارزیابی با پارامترهای داینامیک، چالش و بررسی منطق برنامه.

### حساب‌های توسعه‌ای Seed

| نقش | نام کاربری | رمز عبور |
|---|---|---|
| مدیر | `admin` | `Admin123!` |
| ناظر ۱ | `supervisor1` | `Supervisor123!` |
| ناظر ۲ | `supervisor2` | `Supervisor123!` |
| مشاور ۱ تا ۴ | `advisor1` ... `advisor4` | `Advisor123!` |

این حساب‌ها فقط برای توسعه هستند. در محیط واقعی seed را اجرا نکنید و رمزها را تغییر دهید.

## اجرای تست‌ها با Docker

```bash
docker compose exec backend python manage.py test
```

برای بررسی Django:

```bash
docker compose exec backend python manage.py check
```

برای build فرانت‌اند داخل container:

```bash
docker compose build frontend
```

## توقف سامانه

```bash
docker compose down
```

برای حذف database volume در محیط توسعه:

```bash
docker compose down -v
```

**هشدار:** دستور بالا همه داده‌های PostgreSQL محیط توسعه را حذف می‌کند.

---

# اجرای بدون Docker

## پیش‌نیازها

- Python 3.12 یا بالاتر
- Node.js 22 یا بالاتر
- PostgreSQL 16/17
- npm

## Backend

یک دیتابیس PostgreSQL ایجاد کنید، برای مثال:

```sql
CREATE DATABASE counseling;
CREATE USER counseling WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE counseling TO counseling;
```

سپس:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

متغیرهای محیطی لازم را تنظیم کنید. در اجرای غیر-Docker حتماً `DATABASE_HOST=localhost` باشد.

Linux/macOS نمونه:

```bash
export DJANGO_SECRET_KEY='dev-secret-change-me'
export DJANGO_DEBUG=True
export POSTGRES_DB=counseling
export POSTGRES_USER=counseling
export POSTGRES_PASSWORD='your-password'
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export CORS_ALLOWED_ORIGINS=http://localhost:5173
```

سپس:

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8000
```

## Frontend

در ترمینال دیگر:

```bash
cd frontend
npm install
```

فایل `.env.local` اختیاری:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

سپس:

```bash
npm run dev
```

برای build:

```bash
npm run build
```

## اجرای سریع تست Backend با SQLite

PostgreSQL دیتابیس اصلی سامانه است، اما برای تست محلی مستقل می‌توانید از SQLite موقت استفاده کنید:

```bash
cd backend
USE_SQLITE=True python manage.py test
```

SQLite فقط برای تست/بررسی سریع است و جایگزین PostgreSQL در deployment اصلی نیست.

---

# APIهای مهم

```text
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/logout/

GET/POST/PATCH /api/users/
POST /api/users/{id}/reset-password/
POST /api/users/{id}/temporary-password/

GET/POST/PATCH /api/students/
POST /api/students/{id}/archive/

GET/POST/PATCH /api/weekly-performance/
GET/POST/PATCH /api/assessment-results/
GET/POST/PATCH /api/challenges/
GET /api/program-review-categories/
GET/POST/PATCH /api/program-reviews/
GET /api/activities/

GET /api/dashboard/admin/
GET /api/dashboard/supervisor/
GET /api/dashboard/advisor/
GET /api/dashboard/student/{id}/summary/
GET /api/dashboard/advisor/{id}/summary/
```

همه endpointهای حساس علاوه بر UI، در backend نیز ownership/RBAC را کنترل می‌کنند.

## Pagination و Filtering

Endpointهای لیستی page-based pagination دارند. نمونه:

```text
/api/students/?page=2&search=علی&status=ACTIVE
/api/users/?role=ADVISOR&search=احمد
/api/challenges/?severity=HIGH&status=OPEN
/api/program-reviews/?implementation_status=AWAITING_IMPLEMENTATION&date_from=2026-01-01
/api/assessment-results/?assessment_name=تمرکز&date_from=2026-01-01
```

`page_size` تا سقف 100 قابل تنظیم است.

# امنیت

- Passwordها با password hashing استاندارد Django ذخیره می‌شوند.
- هیچ API رمز قبلی یا password hash را برنمی‌گرداند.
- Access token فقط در حافظه frontend نگهداری می‌شود.
- Refresh token داخل HttpOnly cookie نگهداری می‌شود.
- Logout refresh token را blacklist می‌کند.
- Backend برای Student/WeeklyPerformance/Assessment/Challenge/Review دسترسی object-level اعمال می‌کند.
- شناسه‌ای که browser ارسال می‌کند به‌تنهایی مورد اعتماد نیست.
- CORS از environment تنظیم می‌شود.
- secretها داخل repository hard-code نشده‌اند.
- رکوردهای کسب‌وکاری مهم حذف دائمی نمی‌شوند؛ Student بایگانی و User غیرفعال می‌شود.

## Production hardening

برای production حداقل موارد زیر را انجام دهید:

- `DJANGO_DEBUG=False`
- `COOKIE_SECURE=True`
- HTTPS در reverse proxy/load balancer
- secret واقعی و قوی
- محدود کردن `DJANGO_ALLOWED_HOSTS` و `CORS_ALLOWED_ORIGINS`
- PostgreSQL credential مجزا و قوی
- backup منظم database
- مانیتورینگ application و database
- rate limiting در لایه reverse proxy/API gateway

# RTL و Responsive

UI با `dir="rtl"` ساخته شده و layoutها برای بازه‌های زیر طراحی شده‌اند:

- Mobile: 320–767px
- Tablet: 768–1023px
- Laptop: 1024–1439px
- Desktop: 1440px+

در موبایل sidebar به drawer تبدیل می‌شود، کارت‌های KPI کم‌ستونه می‌شوند، فرم‌ها stack می‌شوند و جدول‌های اصلی یا به کارت تبدیل شده‌اند یا داخل container افقی قابل استفاده هستند.

# رفتار تاریخ

Backend تاریخ‌ها را به‌صورت استاندارد Gregorian/ISO ذخیره می‌کند. Frontend برای نمایش، از `Intl.DateTimeFormat` با تقویم فارسی استفاده می‌کند. Inputهای HTML date در مرورگر همچنان مقدار ISO به API می‌فرستند.

# ارزیابی‌های روان‌شناختی

مدل `AssessmentResult` یک نتیجه بیرونی را ذخیره می‌کند و `AssessmentResultParameter` تعداد متغیری sub-score/parameter دارد. هیچ scale به‌صورت 0 تا 100 فرض نشده است. نمودار score فقط زمانی برای یک نام ارزیابی رسم می‌شود که همان ارزیابی بیش از یک بار ثبت شده باشد؛ ارزیابی‌های ناهم‌مقیاس به‌طور خودکار با هم مقایسه نمی‌شوند.

# بررسی پروژه

اسکریپت زیر بررسی‌های محلی موجود را اجرا می‌کند:

```bash
./scripts/verify.sh
```

این اسکریپت:

1. syntax فایل‌های Python را بررسی می‌کند.
2. در صورت نصب بودن dependencyهای Django، `manage.py check` و testها را اجرا می‌کند.
3. در صورت وجود `node_modules`، build فرانت‌اند را اجرا می‌کند.
4. source را برای placeholderهای ممنوع مانند TODO/FIXME و عبارت‌های MVP/Prototype اسکن می‌کند.


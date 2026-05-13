# TestPlatform — O'qituvchi uchun test platformasi

## Lokal ishga tushirish

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. Migratsiya
python manage.py migrate

# 4. O'qituvchi akkaunt yaratish
python manage.py createsuperuser

# 5. Serverni ishga tushirish
python manage.py runserver
```

Ochiladi: http://127.0.0.1:8000

## Kirish ma'lumotlari (standart)
- O'qituvchi: http://127.0.0.1:8000/teacher/login/
- Login: admin | Parol: admin123

## Deploy (Railway / Render)

settings.py da:
- SECRET_KEY — environment variable qiling
- DEBUG = False
- ALLOWED_HOSTS = ['your-domain.com']
- DATABASES → PostgreSQL (dj-database-url ishlatish mumkin)
- STATIC: whitenoise allaqachon requirements.txt da

## Arxitektura
- models.py   — Test, Question, Choice, Student, Attempt, Answer
- views.py    — o'quvchi + o'qituvchi views
- urls.py     — barcha URL patternlar
- templates/  — HTML shablonlar
- static/css/ — bitta style.css fayl

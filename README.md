# ڕێکخراوی پەروەردەی چیاکان — Django

## دەستپێکردن (یەکجار)
```
python -m venv venv
venv\Scripts\activate          (لە Windows)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
- ماڵپەڕ:  http://127.0.0.1:8000/
- ئەدمین:  http://127.0.0.1:8000/admin-chyakan/

## لە ئەدمین
- **چالاکییەکان**: زیادکردن بە سێ زمان، بەروار (کۆنیش دەبێت) و چەند وێنە (خۆکارانە بچووک دەکرێنەوە).
- **پەیامەکانی پەیوەندی**: هەموو پەیامەکانی فۆڕم، ئەوانەی نەخوێنراون دیاری دەکرێن.
- **ژمارەکانی ماڵپەڕ**: +٣ ، +١ ، +٧٥٠ ، ٢٠٢٦.
- **Users**: ئەو کەسانەی ئەکاونتیان هەیە، ژمارەکەیان لە خوارەوەی لیستەکە.

## بۆ سێرڤەری ڕاستەقینە
متغیرەکان (هەموویان پێویستن):
- `DJANGO_PRODUCTION=1`
- `DJANGO_SECRET_KEY=<کلیلی درێژ و هەڕەمەکی>`  (دەتوانیت بەم شێوەیە دروستی بکەیت: `python -c "import secrets;print(secrets.token_urlsafe(60))"`)
- `DJANGO_HOSTS=دۆمەینەکەت`  و  `DJANGO_ORIGINS=https://دۆمەینەکەت`
- `DB_PASSWORD` (+ `DB_HOST`، `DB_NAME`، `DB_USER` ئەگەر جیاوازن) — PostgreSQL. پاسۆردی داتابەیس هەرگیز لە کۆدەکەدا نانووسرێت.
- `TRUSTED_PROXY_COUNT=1` (ژمارەی پرۆکسی لەپێش Django؛ Render/nginx = 1. ئەگەر Cloudflare ـیش هەبوو = 2)

فەرمانەکان:
- Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start: `gunicorn config.wsgi:application`
- یەکەمجار: `python manage.py createsuperuser`

دیسک (Disk): دوو فۆڵدەر دەبێت هەمیشە بمێننەوە و باکئەپ بکرێن: `media/` (وێنەی چالاکییەکان) و `private_files/` (CVـەکان). ئەگەر سێرڤەرەکە دیسکی بەردەوامی نەبێت، ئەمانە لەگەڵ هەر deployـێک دەسڕێنەوە.

بەکارهێنانی لۆکاڵ: ئەگەر `DB_PASSWORD` دانەنێیت، لە لۆکاڵدا SQLite بەکار دێت. بۆ بەکارهێنانی PostgreSQLی لۆکاڵ، پێش `runserver` ئەمە بنووسە (PowerShell): `$env:DB_PASSWORD="پاسۆردەکەت"`.

## داواکارییەکانی CV و پەیامەکان
- لە ئەدمین: **داواکارییەکانی کار (CV)** ← ناو، ژمارە، ئیمەیل و دوگمەی «دابەزاندن». تەنها ستاف دەتوانێت CV بکاتەوە.
- فایلەکان لە فۆڵدەری `private_files/` هەڵدەگیرێن (بە ناوی هەڕەمەکی)، نەک لە media. لەگەڵ db.sqlite3 باکئەپیان بکە.
- ئاگادارکردنەوە بە ئیمەیل (ئارەزوومەندانە): NOTIFY_EMAIL=ئیمەیلەکەت ، EMAIL_HOST=smtp.gmail.com ، EMAIL_HOST_USER ، EMAIL_HOST_PASSWORD (App Password ی Gmail)

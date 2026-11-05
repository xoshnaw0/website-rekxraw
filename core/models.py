from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import uuid
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

def max5mb(f):
    if f.size > 8 * 1024 * 1024: raise ValidationError("وێنەکە لە 8MB گەورەترە.")

class Activity(models.Model):
    date = models.DateField("بەروار (دەتوانیت تاریخی کۆن بنووسیت)")
    title_ckb = models.CharField("ناونیشان (کوردی)", max_length=200)
    title_ar = models.CharField("ناونیشان (عەرەبی)", max_length=200, blank=True)
    title_en = models.CharField("ناونیشان (ئینگلیزی)", max_length=200, blank=True)
    text_ckb = models.TextField("وەسف (کوردی)", blank=True)
    text_ar = models.TextField("وەسف (عەرەبی)", blank=True)
    text_en = models.TextField("وەسف (ئینگلیزی)", blank=True)
    published = models.BooleanField("بڵاو بکرێتەوە", default=True)
    class Meta:
        ordering = ["-date"]; verbose_name = "چالاکی"; verbose_name_plural = "چالاکییەکان"
    def __str__(self): return f"{self.date} — {self.title_ckb}"

class ActivityImage(models.Model):
    activity = models.ForeignKey(Activity, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField("وێنە", upload_to="activities/%Y/%m/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), max5mb])
    order = models.PositiveSmallIntegerField("ڕیز", default=0)
    class Meta:
        ordering = ["order", "id"]; verbose_name = "وێنە"; verbose_name_plural = "وێنەکان"
    def save(self, *a, **k):
        super().save(*a, **k)
        try:  # shrink big photos; the new file is built in memory first, so the original is never damaged
            import io
            from PIL import Image, ImageOps
            im0 = Image.open(self.image.path); fmt = im0.format; im0.load()
            if fmt not in ("JPEG", "PNG", "WEBP"): return
            im = ImageOps.exif_transpose(im0); im.thumbnail((1600, 1600))
            if fmt == "JPEG" and im.mode not in ("RGB", "L"): im = im.convert("RGB")
            buf = io.BytesIO(); im.save(buf, fmt, quality=82, optimize=True); im0.close()
            with open(self.image.path, "wb") as f: f.write(buf.getvalue())
        except Exception:
            pass

class ContactMessage(models.Model):
    name = models.CharField("ناو", max_length=120)
    email = models.EmailField("ئیمەیل", max_length=180)
    message = models.TextField("پەیام", max_length=1500)
    created = models.DateTimeField("کات", auto_now_add=True)
    is_read = models.BooleanField("خوێنراوەتەوە", default=False)
    class Meta:
        ordering = ["-created"]; verbose_name = "پەیام"; verbose_name_plural = "پەیامەکانی پەیوەندی"
    def __str__(self): return f"{self.name} — {self.created:%Y-%m-%d}"

class SiteStats(models.Model):
    activities_count = models.CharField("کار و چالاکی", max_length=12, default="+3")
    projects_count = models.CharField("پرۆژە", max_length=12, default="+1")
    students_count = models.CharField("قوتابی سوودمەند", max_length=12, default="+750")
    founded = models.CharField("ساڵی دامەزراندن", max_length=12, default="2026")
    class Meta:
        verbose_name = "ژمارەکانی ماڵپەڕ"; verbose_name_plural = "ژمارەکانی ماڵپەڕ"
    def save(self, *a, **k): self.pk = 1; super().save(*a, **k)
    def delete(self, *a, **k): pass
    def __str__(self): return "ژمارەکانی ماڵپەڕ"
    @classmethod
    def get(cls): return cls.objects.get_or_create(pk=1)[0]


def get_private_storage():
    return FileSystemStorage(location=settings.PRIVATE_ROOT, base_url=None)

def cv_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"cv/{uuid.uuid4().hex}.{ext}"   # random name: nobody can guess it

class JobApplication(models.Model):
    name = models.CharField("ناو", max_length=120)
    email = models.EmailField("ئیمەیل", max_length=180)
    phone = models.CharField("ژمارەی مۆبایل", max_length=30)
    field = models.CharField("بواری دڵخواز", max_length=120, blank=True)
    message = models.TextField("دەربارەی خۆی", max_length=1500, blank=True)
    cv = models.FileField("CV", upload_to=cv_path, storage=get_private_storage, max_length=200)
    created = models.DateTimeField("کات", auto_now_add=True)
    is_read = models.BooleanField("بینراوە", default=False)
    class Meta:
        ordering = ["-created"]; verbose_name = "داواکاری کار (CV)"; verbose_name_plural = "داواکارییەکانی کار (CV)"
    def __str__(self): return f"{self.name} — {self.created:%Y-%m-%d}"

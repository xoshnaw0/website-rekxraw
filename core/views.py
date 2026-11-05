import json
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .forms import ContactForm, CVForm
from .models import Activity, ContactMessage, JobApplication


def client_ip(request):
    """Real visitor IP. Behind a proxy REMOTE_ADDR is the proxy, so use X-Forwarded-For,
    counting TRUSTED_PROXY_COUNT entries from the right (the left side can be forged by the visitor)."""
    n = getattr(settings, "TRUSTED_PROXY_COUNT", 1)
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if settings.PROD and xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if len(parts) >= n:
            return parts[-n][:45]
    return request.META.get("REMOTE_ADDR", "?")


def page(name):
    def view(request):
        return render(request, name + ".html")
    return view


@ensure_csrf_cookie
def contact(request):
    return render(request, "contact.html")


def activities_js(request):
    data = [{"date": a.date.isoformat(),
             "title": {"ckb": a.title_ckb, "ar": a.title_ar, "en": a.title_en},
             "text": {"ckb": a.text_ckb, "ar": a.text_ar, "en": a.text_en},
             "images": [i.image.url for i in a.images.all()]}
            for a in Activity.objects.filter(published=True).prefetch_related("images")]
    body = "window.ACTIVITIES = " + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + ";"
    r = HttpResponse(body, content_type="application/javascript; charset=utf-8")
    r["Cache-Control"] = "no-cache"
    return r


def notify(subject, body):
    to = getattr(settings, "NOTIFY_EMAIL", "")
    if to:
        send_mail(subject, body, None, [to], fail_silently=True)


@require_POST
def contact_send(request):
    key = "contact:" + client_ip(request)
    n = cache.get(key, 0)
    if n >= 5:  # max 5 messages / hour / IP
        return JsonResponse({"ok": False}, status=429)
    f = ContactForm(request.POST)
    if not f.is_valid():
        return JsonResponse({"ok": False, "errors": f.errors.get_json_data()}, status=400)
    d = f.cleaned_data
    if d.get("website_url"):  # honeypot filled: pretend OK, save nothing
        return JsonResponse({"ok": True})
    ContactMessage.objects.create(name=d["name"], email=d["email"], message=d["message"])
    cache.set(key, n + 1, 3600)
    notify("Chyakan: new contact message", f"{d['name']} <{d['email']}>\nSee it in the admin panel.")
    return JsonResponse({"ok": True})


@require_POST
def join_send(request):
    key = "cv:" + client_ip(request)
    n = cache.get(key, 0)
    if n >= 3:  # max 3 CVs / hour / IP
        return JsonResponse({"ok": False}, status=429)
    f = CVForm(request.POST, request.FILES)
    if not f.is_valid():
        return JsonResponse({"ok": False, "errors": f.errors.get_json_data()}, status=400)
    d = f.cleaned_data
    if d.get("website_url"):
        return JsonResponse({"ok": True})
    JobApplication.objects.create(name=d["name"], email=d["email"], phone=d["phone"],
                                  field=d["field"], message=d["message"], cv=d["cv"])
    cache.set(key, n + 1, 3600)
    notify("Chyakan: new CV received", f"{d['name']} <{d['email']}>\nSee it in the admin panel.")
    return JsonResponse({"ok": True})


@staff_member_required
def cv_download(request, pk):
    if not request.user.has_perm("core.view_jobapplication"):
        raise PermissionDenied
    a = get_object_or_404(JobApplication, pk=pk)
    ext = a.cv.name.rsplit(".", 1)[-1]
    r = FileResponse(a.cv.open("rb"), as_attachment=True, filename=f"CV-{a.pk}.{ext}")
    r["X-Content-Type-Options"] = "nosniff"
    r["Cache-Control"] = "private, no-store"
    return r
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
CSP = ("default-src 'none'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "img-src 'self' data:; connect-src 'self'; form-action 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'")
class SecurityHeaders:
    def __init__(self, get): self.get = get
    def __call__(self, request):
        r = self.get(request)
        if not request.path.startswith("/" + settings.ADMIN_URL):   # Django admin needs its own inline scripts
            r["Content-Security-Policy"] = CSP
        r["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        return r



class AdminLoginThrottle:
    """Max 10 login attempts / 15 minutes / IP on the admin login page (brute-force protection)."""
    LIMIT, WINDOW = 10, 15 * 60

    def __init__(self, get): self.get = get

    def __call__(self, request):
        if request.method == "POST" and request.path == "/" + settings.ADMIN_URL + "login/":
            from .views import client_ip
            key = "adminlogin:" + client_ip(request)
            n = cache.get(key, 0) + 1
            cache.set(key, n, self.WINDOW)
            if n > self.LIMIT:
                return HttpResponse("Too many login attempts. Try again in 15 minutes.", status=429, content_type="text/plain")
        return self.get(request)

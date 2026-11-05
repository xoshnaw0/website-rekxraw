from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.decorators.cache import cache_control
from django.views.static import serve as _serve
from core.views import cv_download
urlpatterns = [path(settings.ADMIN_URL + "cv/<int:pk>/", cv_download), path(settings.ADMIN_URL, admin.site.urls), path("", include("core.urls"))]
# Activity photos are public. Only /media/activities/... is served (nothing else under media/).
urlpatterns += [re_path(r"^media/(?P<path>activities/.+)$", cache_control(max_age=86400, public=True)(_serve), {"document_root": settings.MEDIA_ROOT})]

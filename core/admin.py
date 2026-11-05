from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from .models import Activity, ActivityImage, ContactMessage, JobApplication, SiteStats
admin.site.site_header = "بەڕێوەبردنی ڕێکخراوی پەروەردەی چیاکان"
admin.site.site_title = "چیاکان"

class ImgInline(admin.TabularInline):
    model = ActivityImage; extra = 3

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("date", "title_ckb", "published"); list_filter = ("published",); search_fields = ("title_ckb", "title_en", "title_ar")
    inlines = [ImgInline]

@admin.register(ContactMessage)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created", "is_read"); list_filter = ("is_read",); search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created"); actions = ["mark_read"]
    def has_add_permission(self, request): return False
    @admin.action(description="نیشانەکردن وەک خوێنراوەتەوە")
    def mark_read(self, request, qs): qs.update(is_read=True)

@admin.register(SiteStats)
class StatsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return not SiteStats.objects.exists()
    def has_delete_permission(self, request, obj=None): return False


@admin.register(JobApplication)
class JobAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "field", "created", "is_read", "cv_link"); list_filter = ("is_read",)
    search_fields = ("name", "email", "phone", "field"); actions = ["mark_read"]
    fields = ("name", "email", "phone", "field", "message", "created", "cv_link", "is_read")
    readonly_fields = ("name", "email", "phone", "field", "message", "created", "cv_link")
    def has_add_permission(self, request): return False
    @admin.display(description="CV")
    def cv_link(self, obj):
        return format_html('<a href="/{}cv/{}/">⬇ دابەزاندن</a>', settings.ADMIN_URL, obj.pk) if obj.pk else "-"
    @admin.action(description="نیشانەکردن وەک بینراوە")
    def mark_read(self, request, qs): qs.update(is_read=True)

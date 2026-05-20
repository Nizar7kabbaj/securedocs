from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "target_repr", "ip_address")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "target_repr", "ip_address")
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)
    readonly_fields = ("user", "action", "target_repr", "ip_address", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
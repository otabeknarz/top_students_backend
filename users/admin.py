from django.contrib import admin
from users.models import User, Invitation


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "username", "has_successfully_registered", "created_at")
    search_fields = ("id", "name", "username")
    list_filter = ("has_successfully_registered", "created_at")
    ordering = ("id",)


admin.site.register(Invitation)

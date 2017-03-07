from django.contrib import admin

from users.models import User as UserProfile, Rol, CustomerProfile


class UserProfileAdmin(admin.ModelAdmin):
    pass


class RolAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'latitude', 'longitude', 'first_dabba',)
    list_editable = ('first_dabba',)
    ordering = ('first_dabba',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Rol, RolAdmin)

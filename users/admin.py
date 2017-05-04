from django.contrib import admin

from users.models import User as UserProfile, Rol, CustomerProfile, UserMovements


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active', 'is_superuser', )
    list_display_links = ('id', 'username', )
    list_editable = ('email', 'is_staff', 'is_active', 'is_superuser')


class RolAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'latitude', 'longitude', 'first_dabba',)
    list_editable = ('first_dabba',)
    ordering = ('first_dabba',)


@admin.register(UserMovements)
class UserMovements(admin.ModelAdmin):
    list_display = ('user', 'category', 'creation_date',)
    ordering = ('creation_date',)


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Rol, RolAdmin)

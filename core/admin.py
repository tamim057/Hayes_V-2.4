from django.contrib import admin
from .models import Duty


@admin.register(Duty)
class DutyAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'is_on_duty', 'total_seconds', 'last_reset', 'start_time')
    list_filter = ('is_on_duty', 'last_reset')
    search_fields = ('user_id',)
    readonly_fields = ('last_reset', 'last_bell')
    fieldsets = (
        ('User Information', {
            'fields': ('user_id',)
        }),
        ('Duty Status', {
            'fields': ('is_on_duty', 'start_time', 'total_seconds')
        }),
        ('Bell System', {
            'fields': ('bell_required', 'last_bell', 'last_cycle')
        }),
        ('Reset Information', {
            'fields': ('last_reset',)
        }),
    )

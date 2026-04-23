from django.contrib import admin
from .models import Academy, OpeningHour, SwimmingPool


class OpeningHourInline(admin.TabularInline):
    model = OpeningHour
    extra = 0


@admin.register(Academy)
class AcademyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_at')
    inlines = [OpeningHourInline]


admin.site.register(SwimmingPool)

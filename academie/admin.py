from django.contrib import admin
from .models import Academy, Course, CourseTiming, Invitation, OpeningHour, Subscription, SwimmingPool


class OpeningHourInline(admin.TabularInline):
    model = OpeningHour
    extra = 0


class CourseTimingInline(admin.TabularInline):
    model = CourseTiming
    extra = 0


@admin.register(Academy)
class AcademyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'created_at')
    list_filter = ('city',)
    search_fields = ('name', 'city')
    inlines = [OpeningHourInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'academy', 'coach', 'level', 'created_at')
    list_filter = ('level', 'academy')
    search_fields = ('name',)
    inlines = [CourseTimingInline]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('from_owner', 'to_coach', 'course', 'status', 'created_at')
    list_filter = ('status',)


admin.site.register(SwimmingPool)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'academy', 'price_at_subscription', 'status', 'subscribed_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'academy__name')

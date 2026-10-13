from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from .models import Movie, MovieReview, OTTAvailability, SeatBooking, Showtime


class OTTInline(admin.TabularInline):
    model = OTTAvailability
    extra = 1


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "poster_thumb",
        "title",
        "industry",
        "language",
        "release_date",
        "in_theatres",
        "is_upcoming",
    )
    list_editable = ("in_theatres", "is_upcoming")
    list_filter = ("in_theatres", "is_upcoming", "industry", "language")
    search_fields = ("title", "genre", "description")
    inlines = [OTTInline]
    fieldsets = (
        ("Movie Information", {
            "fields": ("title", "industry", "language", "genre", "duration", "description")
        }),
        ("Release & Status", {
            "fields": ("release_date", "expected_release", "in_theatres", "is_upcoming")
        }),
        ("Media & Visuals", {
            "fields": ("poster_url", "poster_image", "trailer_url")
        }),
    )

    @admin.display(description="Poster")
    def poster_thumb(self, obj):
        url = obj.poster
        if url:
            return format_html(
                '<img src="{}" style="width: 42px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #444;" />',
                url
            )
        return format_html('<span style="color:#888;">No image</span>')


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ("movie", "show_date", "show_time", "screen_number", "ticket_price", "booked_seats_count")
    list_filter = ("show_date", "screen_number", "movie__industry")
    search_fields = ("movie__title",)

    @admin.display(description="Seats Taken")
    def booked_seats_count(self, obj):
        count = len(obj.booked_seats())
        return f"{count} / 40 seats"


@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "customer_phone",
        "showtime_info",
        "seats",
        "total_paid",
        "status",
        "status_badge",
        "booked_at",
    )
    list_editable = ("status",)
    list_filter = ("status", "showtime__movie", "showtime__show_date", "booked_at")
    search_fields = ("customer_name", "customer_email", "customer_phone", "seats", "showtime__movie__title")
    readonly_fields = ("booked_at", "updated_at")
    actions = ["mark_confirmed", "mark_pending", "mark_cancelled"]

    @admin.display(description="Movie & Time")
    def showtime_info(self, obj):
        return f"{obj.showtime.movie.title} ({obj.showtime.show_date} {obj.showtime.show_time:%H:%M})"

    @admin.display(description="Status View")
    def status_badge(self, obj):
        colors = {
            "CONFIRMED": ("#198754", "#d1e7dd", "#0f5132", "Booked / Confirmed"),
            "PENDING": ("#ffc107", "#fff3cd", "#664d03", "Pending"),
            "CANCELLED": ("#dc3545", "#f8d7da", "#842029", "Cancelled"),
        }
        border, bg, fg, label = colors.get(obj.status, ("#6c757d", "#e2e3e5", "#41464b", obj.status))
        return format_html(
            '<span style="background-color:{}; color:{}; border:1px solid {}; padding:3px 8px; border-radius:12px; font-weight:600; font-size:12px;">{}</span>',
            bg, fg, border, label
        )

    @admin.action(description="Mark selected tickets as Booked / Confirmed")
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status="CONFIRMED")
        self.message_user(request, f"{updated} booking(s) marked as Confirmed.")

    @admin.action(description="Mark selected tickets as Pending")
    def mark_pending(self, request, queryset):
        updated = queryset.update(status="PENDING")
        self.message_user(request, f"{updated} booking(s) marked as Pending.")

    @admin.action(description="Mark selected tickets as Cancelled")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="CANCELLED")
        self.message_user(request, f"{updated} booking(s) marked as Cancelled.")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        confirmed = SeatBooking.objects.filter(status="CONFIRMED")
        pending = SeatBooking.objects.filter(status="PENDING")
        cancelled = SeatBooking.objects.filter(status="CANCELLED")
        total_rev = confirmed.aggregate(Sum("total_paid"))["total_paid__sum"] or 0

        extra_context["stats"] = {
            "confirmed_count": confirmed.count(),
            "pending_count": pending.count(),
            "cancelled_count": cancelled.count(),
            "total_revenue": total_rev,
        }
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "reviewer_name", "rating", "created_at")
    list_filter = ("rating",)


admin.site.register(OTTAvailability)


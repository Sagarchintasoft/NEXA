from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

SEAT_ROWS = "ABCDE"      # 5 rows
SEAT_COLS = range(1, 9)  # 8 columns
MAX_SEATS_PER_BOOKING = 10

PLATFORM_URLS = {
    "Netflix": "https://www.netflix.com/search?q={q}",
    "Prime Video": "https://www.primevideo.com/search/?phrase={q}",
    "JioHotstar": "https://www.hotstar.com/in",
    "ZEE5": "https://www.zee5.com/",
    "SonyLIV": "https://www.sonyliv.com/",
    "aha": "https://www.aha.video/",
    "Apple TV+": "https://tv.apple.com/in",
    "Sun NXT": "https://www.sunnxt.com/",
}


class Movie(models.Model):
    INDUSTRIES = [
        ("Tollywood", "Tollywood (Telugu)"),
        ("Kollywood", "Kollywood (Tamil)"),
        ("Bollywood", "Bollywood (Hindi)"),
        ("Hollywood", "Hollywood (English)"),
    ]
    title = models.CharField(max_length=200)
    industry = models.CharField(max_length=20, choices=INDUSTRIES)
    language = models.CharField(max_length=50, default="Telugu")
    genre = models.CharField(max_length=120, help_text="Comma separated, e.g. Action, Drama")
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    poster_url = models.URLField(blank=True, max_length=500)
    poster_image = models.ImageField(
        upload_to="posters/",
        blank=True,
        null=True,
        help_text="Upload local poster image or leave blank to use poster_url",
    )
    expected_release = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. Summer 2026, Diwali 2026",
    )
    is_upcoming = models.BooleanField(default=False, help_text="Show in 'Upcoming Movies' section")
    trailer_url = models.URLField(blank=True, max_length=500, help_text="YouTube trailer or teaser link")
    description = models.TextField()
    in_theatres = models.BooleanField(
        default=False,
        help_text="Show in 'Now Running' section and allow seat booking",
    )

    class Meta:
        ordering = ["-release_date", "title"]
        unique_together = [("title", "industry")]

    def __str__(self):
        return f"{self.title} ({self.industry})"

    def get_absolute_url(self):
        return reverse("movie_detail", args=[self.pk])

    @property
    def genre_list(self):
        return [g.strip() for g in self.genre.split(",") if g.strip()]

    @property
    def duration_display(self):
        h, m = divmod(self.duration, 60)
        return f"{h}h {m:02d}m"


class OTTAvailability(models.Model):
    PLATFORMS = [(p, p) for p in PLATFORM_URLS]
    ACCESS = [("Subscription", "Subscription"), ("Rent", "Rent / Buy"), ("Free", "Free with ads")]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="streams")
    platform = models.CharField(max_length=30, choices=PLATFORMS)
    access = models.CharField(max_length=20, choices=ACCESS, default="Subscription")
    url = models.URLField(blank=True, help_text="Optional direct link; leave blank for platform search link")

    class Meta:
        unique_together = [("movie", "platform")]
        verbose_name = "OTT availability"
        verbose_name_plural = "OTT availability"

    def __str__(self):
        return f"{self.movie.title} on {self.platform}"

    @property
    def watch_url(self):
        if self.url:
            return self.url
        from urllib.parse import quote_plus
        return PLATFORM_URLS.get(self.platform, "#").format(q=quote_plus(self.movie.title))


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    show_date = models.DateField()
    show_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    screen_number = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["show_date", "show_time", "screen_number"]
        unique_together = [("movie", "show_date", "show_time", "screen_number")]

    def __str__(self):
        return f"{self.movie.title} - {self.show_date} {self.show_time:%H:%M} (Screen {self.screen_number})"

    def booked_seats(self):
        taken = set()
        for seats in self.bookings.exclude(status=SeatBooking.STATUS_CANCELLED).values_list("seats", flat=True):
            taken.update(s for s in seats.split(",") if s)
        return taken


class SeatBooking(models.Model):
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_PENDING = "PENDING"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (STATUS_CONFIRMED, "Booked / Confirmed"),
        (STATUS_PENDING, "Pending"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    seats = models.CharField(max_length=200, help_text="Comma separated, e.g. A1,A2,B5")
    total_paid = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CONFIRMED)
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-booked_at"]

    def __str__(self):
        return f"#{self.pk} {self.customer_name} - {self.seats}"

    @property
    def seat_list(self):
        return [s for s in self.seats.split(",") if s]


class MovieReview(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    reviewer_name = models.CharField(max_length=80)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.movie.title}: {self.rating}/5 by {self.reviewer_name}"

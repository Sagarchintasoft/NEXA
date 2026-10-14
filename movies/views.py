from django.contrib import messages
from django.db import transaction
from django.db.models import Avg, Count, Exists, OuterRef, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookingForm, ReviewForm
from .models import (
    MAX_SEATS_PER_BOOKING, Movie, OTTAvailability, SEAT_COLS, SEAT_ROWS, SeatBooking, Showtime,
)


def movie_list(request):
    """Home page + OTT/theatre search engine (supports live AJAX filtering)."""
    now = timezone.localtime()
    q = request.GET.get("q", "").strip()
    industry = request.GET.get("industry", "")
    genre = request.GET.get("genre", "")
    platform = request.GET.get("platform", "")
    show = request.GET.get("show", "")

    upcoming_showtimes = Showtime.objects.filter(movie_id=OuterRef("pk")).filter(
        Q(show_date__gt=now.date()) | Q(show_date=now.date(), show_time__gt=now.time())
    )
    qs = Movie.objects.annotate(
        avg_rating=Avg("reviews__rating"),
        review_count=Count("reviews"),
        has_showtimes=Exists(upcoming_showtimes),
    ).prefetch_related("streams")

    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(genre__icontains=q)
            | Q(language__icontains=q)
            | Q(description__icontains=q)
            | Q(id__in=OTTAvailability.objects.filter(platform__icontains=q).values("movie_id"))
        )
    if industry in dict(Movie.INDUSTRIES):
        qs = qs.filter(industry=industry)
    if genre:
        qs = qs.filter(genre__icontains=genre)
    if platform in dict(OTTAvailability.PLATFORMS):
        qs = qs.filter(id__in=OTTAvailability.objects.filter(platform=platform).values("movie_id"))
    if show == "theatres":
        qs = qs.filter(in_theatres=True, release_date__lte=now.date())
    elif show == "upcoming":
        qs = qs.filter(is_upcoming=True, release_date__gt=now.date())
    elif show == "streaming":
        qs = qs.filter(id__in=OTTAvailability.objects.values("movie_id"))

    movies = list(qs)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "movies/_movie_grid.html", {"movies": movies})

    all_genres = sorted({g.strip() for gs in Movie.objects.values_list("genre", flat=True) for g in gs.split(",") if g.strip()})
    used_platforms = (
        OTTAvailability.objects.order_by("platform").values_list("platform", flat=True).distinct()
    )
    show_sections = not any((q, industry, genre, platform, show))
    section_movies = Movie.objects.annotate(
        avg_rating=Avg("reviews__rating"),
        review_count=Count("reviews"),
        has_showtimes=Exists(upcoming_showtimes),
    ).prefetch_related("streams")
    return render(request, "movies/movie_list.html", {
        "movies": movies,
        "show_sections": show_sections,
        "now_running_movies": section_movies.filter(
            in_theatres=True, release_date__lte=now.date()
        ),
        "upcoming_movies": section_movies.filter(
            is_upcoming=True, release_date__gt=now.date()
        ),
        "industries": Movie.INDUSTRIES,
        "genres": all_genres,
        "platforms": used_platforms,
        "f": {"q": q, "industry": industry, "genre": genre, "platform": platform, "show": show},
    })


def movie_detail(request, pk):
    movie = get_object_or_404(
        Movie.objects.annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews")), pk=pk
    )
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.save()
            messages.success(request, "Thanks! Your review has been posted.")
            return redirect("movie_detail", pk=movie.pk)
    else:
        form = ReviewForm()

    now = timezone.localtime()
    showtimes = movie.showtimes.none()
    if movie.in_theatres or movie.is_upcoming:
        showtimes = movie.showtimes.filter(
            Q(show_date__gt=now.date()) | Q(show_date=now.date(), show_time__gt=now.time())
        )
    return render(request, "movies/movie_detail.html", {
        "movie": movie,
        "showtimes": showtimes,
        "reviews": movie.reviews.all(),
        "streams": movie.streams.all(),
        "form": form,
    })


def book_seats(request, showtime_id):
    showtime = get_object_or_404(Showtime.objects.select_related("movie"), pk=showtime_id)
    if not showtime.movie.in_theatres and not showtime.movie.is_upcoming:
        raise Http404

    if request.method == "POST":
        # Validation (including the duplicate-seat check) and the insert run in one
        # transaction; SQLite serialises writers so two people can't both win a seat.
        with transaction.atomic():
            form = BookingForm(request.POST, showtime=showtime)
            if form.is_valid():
                seats = form.cleaned_data["seats"]
                booking = SeatBooking.objects.create(
                    showtime=showtime,
                    customer_name=form.cleaned_data["customer_name"],
                    customer_email=form.cleaned_data["customer_email"],
                    customer_phone=form.cleaned_data["customer_phone"],
                    seats=",".join(seats),
                    total_paid=showtime.ticket_price * len(seats),  # price computed on the server
                    status=SeatBooking.STATUS_PENDING,
                )
                mine = request.session.get("my_bookings", [])
                request.session["my_bookings"] = mine + [booking.pk]
                return redirect("booking_success", pk=booking.pk)
    else:
        form = BookingForm(showtime=showtime)

    return render(request, "movies/book.html", {
        "showtime": showtime,
        "form": form,
        "booked": sorted(showtime.booked_seats()),
        "rows": list(SEAT_ROWS),
        "cols": list(SEAT_COLS),
        "max_seats": MAX_SEATS_PER_BOOKING,
    })


def booking_success(request, pk):
    booking = get_object_or_404(SeatBooking.objects.select_related("showtime__movie"), pk=pk)
    if pk not in request.session.get("my_bookings", []) and not request.user.is_staff:
        raise Http404
    return render(request, "movies/booking_success.html", {"booking": booking})

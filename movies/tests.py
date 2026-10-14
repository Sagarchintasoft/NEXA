from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Movie, SeatBooking, Showtime


class SeededPosterCoverageTests(TestCase):
    def test_seed_command_adds_a_poster_for_every_movie(self):
        call_command("seed_movies", stdout=StringIO())

        self.assertFalse(Movie.objects.filter(poster_url="").exists())


class MovieSectionsTests(TestCase):
    def setUp(self):
        today = timezone.localdate()
        self.running_movie = Movie.objects.create(
            title="Now Running Test",
            industry="Tollywood",
            genre="Drama",
            duration=120,
            release_date=today - timedelta(days=1),
            description="Currently showing.",
            in_theatres=True,
        )
        self.upcoming_movie = Movie.objects.create(
            title="Upcoming Test",
            industry="Tollywood",
            genre="Action",
            duration=130,
            release_date=today + timedelta(days=2),
            description="Coming soon.",
            is_upcoming=True,
        )

    def test_home_page_has_separate_running_and_upcoming_sections(self):
        response = self.client.get(reverse("movie_list"))

        self.assertContains(response, "Now Running")
        self.assertContains(response, "Upcoming Movies")
        self.assertContains(response, self.running_movie.title)
        self.assertContains(response, self.upcoming_movie.title)

    def test_upcoming_filter_excludes_running_movies(self):
        response = self.client.get(reverse("movie_list"), {"show": "upcoming"})

        self.assertContains(response, self.upcoming_movie.title)
        self.assertNotContains(response, self.running_movie.title)


class SeatBookingStatusTests(TestCase):
    def test_non_running_movie_showtime_cannot_be_booked(self):
        movie = Movie.objects.create(
            title="Past Movie",
            industry="Tollywood",
            genre="Drama",
            duration=120,
            release_date=timezone.localdate() - timedelta(days=30),
            description="No longer in theatres.",
        )
        showtime = Showtime.objects.create(
            movie=movie,
            show_date=timezone.localdate() + timedelta(days=1),
            show_time="18:30",
            ticket_price=Decimal("200.00"),
            screen_number=1,
        )

        response = self.client.get(reverse("book", args=[showtime.pk]))

        self.assertEqual(response.status_code, 404)

    def test_new_booking_is_pending_and_cancelled_seats_are_released(self):
        movie = Movie.objects.create(
            title="Booking Test",
            industry="Tollywood",
            genre="Drama",
            duration=120,
            release_date=timezone.localdate(),
            description="Test movie.",
            in_theatres=True,
        )
        showtime = Showtime.objects.create(
            movie=movie,
            show_date=timezone.localdate() + timedelta(days=1),
            show_time="18:30",
            ticket_price=Decimal("200.00"),
            screen_number=1,
        )

        response = self.client.post(reverse("book", args=[showtime.pk]), {
            "customer_name": "Test Customer",
            "customer_email": "customer@example.com",
            "customer_phone": "9876543210",
            "seats": "A1",
        })

        self.assertEqual(response.status_code, 302)
        booking = SeatBooking.objects.get()
        self.assertEqual(booking.status, SeatBooking.STATUS_PENDING)
        self.assertEqual(showtime.booked_seats(), {"A1"})
        success_response = self.client.get(response["Location"])
        self.assertContains(success_response, "Booking request received")
        self.assertContains(success_response, "Pending")

        booking.status = SeatBooking.STATUS_CANCELLED
        booking.save()

        self.assertEqual(showtime.booked_seats(), set())
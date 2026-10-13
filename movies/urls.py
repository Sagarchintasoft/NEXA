from django.urls import path

from . import views

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("movie/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("book/<int:showtime_id>/", views.book_seats, name="book"),
    path("booking/<int:pk>/", views.booking_success, name="booking_success"),
]

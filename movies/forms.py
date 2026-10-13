import re

from django import forms
from django.core.validators import RegexValidator

from .models import MAX_SEATS_PER_BOOKING, MovieReview, SEAT_COLS, SEAT_ROWS

SEAT_RE = re.compile(rf"^[{SEAT_ROWS}][{min(SEAT_COLS)}-{max(SEAT_COLS)}]$")


def seat_sort_key(seat):
    return (seat[0], int(seat[1:]))


class BookingForm(forms.Form):
    customer_name = forms.CharField(max_length=100, label="Full name")
    customer_email = forms.EmailField(label="Email")
    customer_phone = forms.CharField(
        max_length=15,
        label="Phone",
        validators=[RegexValidator(r"^\+?\d{10,14}$", "Enter a valid phone number (10-14 digits).")],
    )
    seats = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, showtime=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.showtime = showtime
        for name in ("customer_name", "customer_email", "customer_phone"):
            self.fields[name].widget.attrs["class"] = "form-control"

    def clean_seats(self):
        raw = self.cleaned_data["seats"]
        seats = [s.strip().upper() for s in raw.split(",") if s.strip()]
        if not seats:
            raise forms.ValidationError("Please select at least one seat.")
        if len(seats) > MAX_SEATS_PER_BOOKING:
            raise forms.ValidationError(f"You can book at most {MAX_SEATS_PER_BOOKING} seats at a time.")
        if len(set(seats)) != len(seats):
            raise forms.ValidationError("Duplicate seats in selection.")
        invalid = [s for s in seats if not SEAT_RE.match(s)]
        if invalid:
            raise forms.ValidationError(f"Invalid seat(s): {', '.join(invalid)}")
        taken = self.showtime.booked_seats() & set(seats)
        if taken:
            raise forms.ValidationError(
                "Sorry, these seats were just booked by someone else: "
                + ", ".join(sorted(taken, key=seat_sort_key))
                + ". Please pick different seats."
            )
        return sorted(seats, key=seat_sort_key)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = MovieReview
        fields = ["reviewer_name", "rating", "comment"]
        widgets = {
            "reviewer_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "rating": forms.HiddenInput(),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "What did you think?"}),
        }
        error_messages = {
            "rating": {
                "required": "Please choose a rating from 1 to 5 stars.",
                "min_value": "Rating must be between 1 and 5.",
                "max_value": "Rating must be between 1 and 5.",
            }
        }

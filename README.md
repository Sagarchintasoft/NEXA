# NEXA | NEXAFILCK - Movie Ticket Booking, Reviews & OTT Search (Django + SQLite)

Tollywood, Bollywood and Hollywood movies, 5x8 seat booking, 1-5 star reviews and an OTT streaming search engine.

## Run locally
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations movies
python manage.py migrate
python manage.py seed_movies      # sample movies + posters + OTT data + showtimes + reviews
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/  (admin: /admin/)

## Deploy on Render
1. `git init && git add . && git commit -m "Prepare Django project for Render" && git push origin main`
2. Render -> New + -> Blueprint (uses render.yaml) -> connect repo.
3. In the service's Environment tab set `DJANGO_SUPERUSER_PASSWORD`.
4. Commit the `movies/migrations/0001_initial.py` created by makemigrations.

SQLite on Render's free tier is ephemeral: data resets on redeploy/restart. The start command re-runs
`migrate`, `create_superuser.py` and `seed_movies` so the demo is always populated.

## Notes
- OTT availability is sample data (it changes often) - edit it under Admin -> Movies -> OTT availability.
- Edit Now Running and Upcoming Movies flags, release dates, showtimes, and poster URLs under Admin -> Movies.
- Upload a poster image in Admin or use a direct poster URL; the uploaded image takes priority.
- New ticket bookings start as Pending. In Admin -> Seat bookings, staff can mark tickets Booked / Confirmed, leave them Pending, or Cancel them. Cancelled seats become available again.

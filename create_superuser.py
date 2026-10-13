"""Creates an admin user from environment variables (idempotent)."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinema.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")

if not password:
    print("DJANGO_SUPERUSER_PASSWORD not set - skipping superuser creation.")
elif User.objects.filter(username=username).exists():
    print(f"Superuser '{username}' already exists.")
else:
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created.")

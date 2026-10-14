from django.db import migrations


LEGACY_THEATRE_TITLES = [
    "Pushpa 2: The Rule",
    "Kalki 2898 AD",
    "Salaar: Part 1 - Ceasefire",
    "Devara: Part 1",
    "Jawan",
    "Stree 2",
    "Chhaava",
    "Saiyaara",
    "Avatar: The Way of Water",
    "Spider-Man: No Way Home",
    "Dune: Part Two",
    "Deadpool & Wolverine",
]


def mark_legacy_movies_not_running(apps, schema_editor):
    movie_model = apps.get_model("movies", "Movie")
    movie_model.objects.filter(
        title__in=LEGACY_THEATRE_TITLES,
        in_theatres=True,
    ).update(in_theatres=False)


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0003_alter_movie_industry"),
    ]

    operations = [
        migrations.RunPython(mark_legacy_movies_not_running, migrations.RunPython.noop),
    ]
"""Idempotent sample data: Tollywood + Bollywood + Hollywood movies, OTT availability,
upcoming showtimes (refreshed every run) and a few reviews.

OTT availability changes often - treat it as sample data and edit it in /admin/."""
from datetime import date, time, timedelta

from django.core.management.base import BaseCommand

from movies.models import Movie, MovieReview, OTTAvailability, Showtime

N, P, H, Z, S, A = "Netflix", "Prime Video", "JioHotstar", "ZEE5", "SonyLIV", "aha"

# (title, industry, language, genre, minutes, release date, description, in_theatres, [(platform, access)])
MOVIES = [
    # ---------------- Tollywood ----------------
    ("RRR", "Tollywood", "Telugu", "Action, Drama", 187, date(2022, 3, 25),
     "Two revolutionaries, Alluri Sitarama Raju and Komaram Bheem, forge an epic friendship in pre-independence India.", False, [(N, "Subscription"), (Z, "Subscription")]),
    ("Pushpa 2: The Rule", "Tollywood", "Telugu", "Action, Crime", 200, date(2024, 12, 5),
     "Pushpa Raj faces off with the system and old enemies as his red sanders empire grows.", True, [(N, "Subscription")]),
    ("Pushpa: The Rise", "Tollywood", "Telugu", "Action, Crime", 179, date(2021, 12, 17),
     "A labourer rises through the red sandalwood smuggling syndicate of Seshachalam.", False, [(P, "Subscription")]),
    ("Kalki 2898 AD", "Tollywood", "Telugu", "Sci-Fi, Action", 181, date(2024, 6, 27),
     "A futuristic mythological epic where a bounty hunter gets drawn into the fate of the world's last city.", True, [(P, "Subscription"), (N, "Subscription")]),
    ("Salaar: Part 1 - Ceasefire", "Tollywood", "Telugu", "Action, Thriller", 175, date(2023, 12, 22),
     "Two friends turn bitter rivals in the violent, fictional city-state of Khansaar.", True, [(N, "Subscription"), (H, "Subscription")]),
    ("Devara: Part 1", "Tollywood", "Telugu", "Action, Drama", 178, date(2024, 9, 27),
     "A coastal-land fearless leader fights to keep smugglers away from the sea.", True, [(N, "Subscription")]),
    ("HanuMan", "Tollywood", "Telugu", "Fantasy, Action", 158, date(2024, 1, 12),
     "An ordinary man gains the powers of Lord Hanuman and must defend his village.", False, [(Z, "Subscription"), (H, "Subscription")]),
    ("Sita Ramam", "Tollywood", "Telugu", "Romance, Drama", 163, date(2022, 8, 5),
     "A soldier's letters from 1964 lead a young woman on a journey to find his lost love.", False, [(P, "Subscription")]),
    ("Ala Vaikunthapurramuloo", "Tollywood", "Telugu", "Comedy, Drama", 165, date(2020, 1, 12),
     "A man raised in a middle-class home discovers he was swapped at birth with a rich businessman's son.", False, [(N, "Subscription"), ("Sun NXT", "Subscription")]),
    ("Baahubali 2: The Conclusion", "Tollywood", "Telugu", "Action, Epic", 167, date(2017, 4, 28),
     "Shivudu learns why Kattappa killed Baahubali and sets out to reclaim Mahishmati.", False, [(N, "Subscription")]),
    ("Mahanati", "Tollywood", "Telugu", "Biography, Drama", 177, date(2018, 5, 9),
     "The life of legendary actress Savitri, from stardom to tragedy.", False, [(P, "Subscription")]),
    ("Lucky Baskhar", "Tollywood", "Telugu", "Crime, Drama", 150, date(2024, 10, 31),
     "A modest bank cashier gets entangled in a high-stakes money scheme in 1990s Bombay.", False, [(N, "Subscription")]),
    # ---------------- Bollywood ----------------
    ("Jawan", "Bollywood", "Hindi", "Action, Thriller", 169, date(2023, 9, 7),
     "A man driven by a personal vendetta sets out to right the wrongs of society.", True, [(N, "Subscription")]),
    ("Pathaan", "Bollywood", "Hindi", "Action, Spy", 146, date(2023, 1, 25),
     "An exiled Indian agent returns to take on a private terror group.", False, [(P, "Subscription")]),
    ("Animal", "Bollywood", "Hindi", "Action, Crime", 201, date(2023, 12, 1),
     "A son's obsessive love for his father spirals into violence and vengeance.", False, [(N, "Subscription")]),
    ("Stree 2", "Bollywood", "Hindi", "Horror, Comedy", 147, date(2024, 8, 15),
     "The town of Chanderi faces a new, headless terror and the gang must save it again.", True, [(P, "Subscription")]),
    ("Chhaava", "Bollywood", "Hindi", "Historical, Action", 161, date(2025, 2, 14),
     "The story of Chhatrapati Sambhaji Maharaj, successor of Shivaji.", True, [(N, "Subscription")]),
    ("Saiyaara", "Bollywood", "Hindi", "Romance, Drama", 156, date(2025, 7, 18),
     "A troubled musician and a shy lyricist find love and music together.", True, [(N, "Subscription")]),
    ("Dangal", "Bollywood", "Hindi", "Biography, Sport", 161, date(2016, 12, 23),
     "Mahavir Singh Phogat trains his daughters to become world-class wrestlers.", False, [(H, "Subscription")]),
    ("3 Idiots", "Bollywood", "Hindi", "Comedy, Drama", 170, date(2009, 12, 25),
     "Three engineering students navigate friendship, pressure and the search for real learning.", False, [(P, "Subscription")]),
    ("Laapataa Ladies", "Bollywood", "Hindi", "Comedy, Drama", 124, date(2024, 3, 1),
     "Two brides get swapped on a train, setting off a warm, funny search across rural India.", False, [(N, "Subscription")]),
    ("12th Fail", "Bollywood", "Hindi", "Biography, Drama", 147, date(2023, 10, 27),
     "The true story of IPS officer Manoj Kumar Sharma's struggle to crack the UPSC exam.", False, [(H, "Subscription")]),
    ("Gully Boy", "Bollywood", "Hindi", "Musical, Drama", 153, date(2019, 2, 14),
     "A street rapper from Mumbai's slums fights to turn his passion into a career.", False, [(P, "Subscription")]),
    ("Bajrangi Bhaijaan", "Bollywood", "Hindi", "Comedy, Drama", 163, date(2015, 7, 17),
     "A devout man sets out to reunite a lost mute Pakistani girl with her family.", False, [(Z, "Subscription")]),
    # ---------------- Hollywood ----------------
    ("Avengers: Endgame", "Hollywood", "English", "Superhero, Action", 181, date(2019, 4, 26),
     "The Avengers assemble one last time to undo Thanos's snap.", False, [(H, "Subscription")]),
    ("Avatar: The Way of Water", "Hollywood", "English", "Sci-Fi, Adventure", 192, date(2022, 12, 16),
     "Jake Sully and his family flee to the reef clans of Pandora as an old threat returns.", True, [(H, "Subscription")]),
    ("Spider-Man: No Way Home", "Hollywood", "English", "Superhero, Action", 148, date(2021, 12, 17),
     "Peter Parker asks Doctor Strange for help and opens the multiverse.", True, [(N, "Subscription")]),
    ("The Dark Knight", "Hollywood", "English", "Action, Crime", 152, date(2008, 7, 18),
     "Batman faces the Joker, a criminal mastermind who wants to plunge Gotham into chaos.", False, [(H, "Subscription")]),
    ("Inception", "Hollywood", "English", "Sci-Fi, Thriller", 148, date(2010, 7, 16),
     "A thief who steals secrets from dreams is offered a chance to plant an idea instead.", False, [(N, "Subscription")]),
    ("Interstellar", "Hollywood", "English", "Sci-Fi, Drama", 169, date(2014, 11, 7),
     "Explorers travel through a wormhole in search of a new home for humanity.", False, [(P, "Rent")]),
    ("Oppenheimer", "Hollywood", "English", "Biography, Drama", 180, date(2023, 7, 21),
     "The story of J. Robert Oppenheimer and the creation of the atomic bomb.", False, [(P, "Rent")]),
    ("Dune: Part Two", "Hollywood", "English", "Sci-Fi, Adventure", 166, date(2024, 3, 1),
     "Paul Atreides unites with the Fremen to avenge his family and prevent a terrible future.", True, [(H, "Subscription")]),
    ("Deadpool & Wolverine", "Hollywood", "English", "Superhero, Comedy", 128, date(2024, 7, 26),
     "Deadpool is recruited by the TVA and teams up with a reluctant Wolverine.", True, [(H, "Subscription")]),
    ("Barbie", "Hollywood", "English", "Comedy, Fantasy", 114, date(2023, 7, 21),
     "Barbie leaves Barbieland for the real world and discovers what it means to be human.", False, [(H, "Subscription")]),
    ("Joker", "Hollywood", "English", "Crime, Drama", 122, date(2019, 10, 4),
     "A failed comedian descends into madness and becomes Gotham's Clown Prince of Crime.", False, [(H, "Subscription")]),
    ("Top Gun: Maverick", "Hollywood", "English", "Action, Drama", 130, date(2022, 5, 27),
     "After 30 years, Maverick trains a new generation of pilots for a near-impossible mission.", False, [(H, "Subscription")]),
]

REVIEWS = [
    ("Ravi", 5, "Mass entertainment from start to end. Loved the visuals!"),
    ("Ananya", 4, "Great performances and a strong story. Slightly long but worth it."),
    ("Kiran", 4, "Solid watch with the family. Music was fantastic."),
]
PRICE = {"Tollywood": 200, "Bollywood": 220, "Hollywood": 300}
SLOTS = [time(10, 30), time(14, 0), time(18, 30), time(21, 45)]


class Command(BaseCommand):
    help = "Load sample movies, OTT availability, upcoming showtimes and reviews (safe to re-run)."

    def handle(self, *args, **options):
        today = date.today()
        created = 0
        for i, (title, industry, lang, genre, mins, rel, desc, theatres, ott) in enumerate(MOVIES):
            movie, was_new = Movie.objects.get_or_create(
                title=title, industry=industry,
                defaults=dict(language=lang, genre=genre, duration=mins, release_date=rel,
                              description=desc, in_theatres=theatres),
            )
            created += was_new
            for platform, access in ott:
                OTTAvailability.objects.get_or_create(movie=movie, platform=platform, defaults={"access": access})

            if movie.in_theatres:
                screen = (movie.pk % 4) + 1
                for d in range(3):
                    for j, t in enumerate(SLOTS[(i % 2): (i % 2) + 3]):
                        price = PRICE[industry] + (50 if t.hour >= 18 else 0)
                        Showtime.objects.get_or_create(
                            movie=movie, show_date=today + timedelta(days=d), show_time=t,
                            screen_number=screen, defaults={"ticket_price": price},
                        )
            if was_new and i % 3 == 0:
                for name, rating, comment in REVIEWS[: 1 + i % 3]:
                    MovieReview.objects.create(movie=movie, reviewer_name=name, rating=rating, comment=comment)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {Movie.objects.count()} movies ({created} new), "
            f"{Showtime.objects.count()} showtimes."))

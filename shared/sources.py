# shared/sources.py

import random
import datetime

def fetch_conditions_for_resort(resort):
    """
    Zwraca SUROWE dane + nazwę źródła
    """

    # MOCK – później podmienisz na scraping / API
    raw = {
        "open": True,
        "snow_cm": random.randint(20, 80),

        "trails_open": random.randint(3, 10),
        "trails_total": 12,

        "lifts_open": random.randint(2, 6),
        "lifts_total": 8,

        "temp_c": random.randint(-10, 2),
        "wind_kmh": random.randint(0, 30),
        "weather_desc": random.choice(["śnieg", "pochmurno", "słonecznie"]),

        "last_grooming": (
            datetime.datetime.utcnow()
            .replace(hour=21, minute=0, second=0)
            .isoformat() + "Z"
        ),

        "confidence": 0.6
    }

    source_name = "mock"

    return raw, source_name

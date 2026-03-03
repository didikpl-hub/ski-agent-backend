from bs4 import BeautifulSoup
from datetime import datetime, timezone
from .browser import fetch_html


ARLAMOW_URL = "https://www.arlamow.pl/"


def fetch_arlamow():
    html = fetch_html(ARLAMOW_URL)
    soup = BeautifulSoup(html, "html.parser")

    # 🔍 Tu będziemy dopasowywać realne selektory
    text = soup.get_text().lower()

    now = datetime.now(timezone.utc)

    # --- STATUS ---
    is_open = "zamknięty" not in text

    # --- ŚNIEG (placeholder – dopasujemy selektor później) ---
    snow_cm = None

    # --- TRASY ---
    # Arłamów ma ~1.6 km tras (same łatwe)
    open_slopes = {
        "green_km": 1.6 if is_open else 0,
        "blue_km": 0,
        "red_km": 0,
        "black_km": 0,
    }

    # --- WYCIĄGI ---
    total_lifts = 3
    lifts_open = 3 if is_open else 0

    raw = {
        "open": is_open,
        "snow_cm": snow_cm,
        "open_slopes": open_slopes,
        "lifts_open": lifts_open,
        "temp_c": None,
        "wind_kmh": None,
        "weather_desc": None,
        "last_grooming": None,
        "confidence": 0.6,
    }

    return raw, "scraper:arlamow"
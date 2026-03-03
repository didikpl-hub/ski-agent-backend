from datetime import datetime
from shared.schema import empty_conditions_record


def normalize_conditions(raw: dict, resort: dict = None, source: str = "unknown", **kwargs) -> dict:
    """
    Normalizuje surowe dane warunków dla jednego resortu.
    Przechowujemy TYLKO dane dynamiczne.
    """

    record = empty_conditions_record()

    # --- ID ---
    if resort and "id" in resort:
        record["id"] = resort["id"]

    # --- STATUS ---
    open_val = raw.get("open")
    if open_val is True:
        record["status"] = "open"
    elif open_val is False:
        record["status"] = "closed"
    else:
        record["status"] = "unknown"

    # --- ŚNIEG ---
    record["snow_depth_cm"] = raw.get("snow_cm")

    # --- POGODA ---
    record["weather"]["temperature_c"] = raw.get("temp_c")
    record["weather"]["wind_kmh"] = raw.get("wind_kmh")
    record["weather"]["conditions"] = raw.get("weather_desc")

    # --- OTWARTE WYCIĄGI (tylko open, bez total) ---
    record["open_lifts"] = raw.get("lifts_open")

    # --- OPEN SLOPES (na przyszłość, jeśli źródło poda kolory) ---
    if "open_slopes" in raw:
        record["open_slopes"] = raw["open_slopes"]

    # --- RATRAK ---
    record["last_grooming"] = raw.get("last_grooming")

    # --- META ---
    record["data_quality"]["source"] = source
    record["data_quality"]["confidence"] = raw.get("confidence")
    record["data_quality"]["stale"] = False

    record["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return record
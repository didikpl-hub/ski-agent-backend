SCHEMA_VERSION = "2.0"


def empty_conditions_record():
    return {
        "_schema_version": SCHEMA_VERSION,

        # --------------------
        # STATUS
        # --------------------
        "status": "unknown",  # open / closed / unknown

        # --------------------
        # ŚNIEG
        # --------------------
        "snow_depth_cm": None,

        # --------------------
        # OTWARTE TRASY (Opcja B – per kolor)
        # wartości w km
        # None = brak danych
        # 0 = wiemy że brak
        # --------------------
        "open_slopes": {
            "green_km": None,
            "blue_km": None,
            "red_km": None,
            "black_km": None
        },

        # --------------------
        # OTWARTE WYCIĄGI (tylko liczba open)
        # --------------------
        "open_lifts": None,

        # --------------------
        # POGODA
        # --------------------
        "weather": {
            "temperature_c": None,
            "wind_kmh": None,
            "conditions": None
        },

        # --------------------
        # RATRAK
        # --------------------
        "last_grooming": None,

        # --------------------
        # METADANE
        # --------------------
        "data_quality": {
            "source": None,
            "stale": True
        },

        # timestamp ustawiany w normalize
        "updated_at": None
    }

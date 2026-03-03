import json
import logging
from azure.storage.blob import BlobServiceClient
import os

# --- Konfiguracja ---
CONNECTION_STRING = os.environ.get(
    "AzureWebJobsStorage",
    "UseDevelopmentStorage=true"
)

RESORTS_CONTAINER = "data"
RESORTS_BLOB = "resorts.json"
CONDITIONS_BLOB = "conditions.json"


# =====================================================
# Container
# =====================================================

def get_container_client(container_name=RESORTS_CONTAINER):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(container_name)

        if not container_client.exists():
            logging.info(f"📦 Kontener '{container_name}' nie istnieje – tworzę go...")
            container_client.create_container()

        return container_client

    except Exception as e:
        logging.error(f"❌ Błąd inicjalizacji container_client: {e}")
        raise


# =====================================================
# RESORTS
# =====================================================

def load_resorts():
    """
    Wczytuje resorts.json.
    Obsługuje:
      1) starą strukturę: [ ... ]
      2) nową strukturę: { "ski_resorts": [ ... ] }
    """
    try:
        container_client = get_container_client()
        blob_client = container_client.get_blob_client(RESORTS_BLOB)

        if not blob_client.exists():
            logging.warning(f"⚠ {RESORTS_BLOB} nie istnieje – zwracam pustą listę")
            return []

        data = blob_client.download_blob().readall()

        if not data:
            logging.warning("⚠ resorts.json jest pusty")
            return []

        parsed = json.loads(data)

        # NOWA STRUKTURA
        if isinstance(parsed, dict) and "ski_resorts" in parsed:
            logging.info(f"📂 Załadowano {len(parsed['ski_resorts'])} resortów (nowa struktura)")
            return parsed["ski_resorts"]

        # STARA STRUKTURA
        if isinstance(parsed, list):
            logging.info(f"📂 Załadowano {len(parsed)} resortów (stara struktura)")
            return parsed

        logging.warning("⚠ Nieznany format resorts.json – zwracam pustą listę")
        return []

    except Exception as e:
        logging.error(f"❌ Failed to load resorts: {e}")
        return []


# =====================================================
# CONDITIONS
# =====================================================

def load_conditions():
    """
    Wczytuje conditions.json.
    Zwraca dict { resort_id: conditions }
    """
    try:
        container_client = get_container_client()
        blob_client = container_client.get_blob_client(CONDITIONS_BLOB)

        if not blob_client.exists():
            logging.info("ℹ conditions.json nie istnieje – zwracam pusty dict")
            return {}

        data = blob_client.download_blob().readall()

        if not data:
            logging.warning("⚠ conditions.json jest pusty")
            return {}

        parsed = json.loads(data)

        if isinstance(parsed, dict):
            return parsed

        logging.warning("⚠ Nieznany format conditions.json")
        return {}

    except Exception as e:
        logging.error(f"❌ Failed to load conditions: {e}")
        return {}


def save_conditions(conditions: dict):
    """
    Zapisuje conditions.json jako:
    {
      "resort_id": {...},
      ...
    }
    """
    try:
        container_client = get_container_client()
        blob_client = container_client.get_blob_client(CONDITIONS_BLOB)

        payload = json.dumps(
            conditions,
            ensure_ascii=False,
            indent=2
        )

        blob_client.upload_blob(payload, overwrite=True)

        logging.info(f"💾 Zapisano {len(conditions)} warunków do {CONDITIONS_BLOB}")

    except Exception as e:
        logging.error(f"❌ Failed to save conditions: {e}")
        raise

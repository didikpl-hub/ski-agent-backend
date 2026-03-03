import os
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient

from shared.sources_arlamow import fetch_arlamow
from shared.normalize import normalize_conditions


def main():
    print("=== START SCRAPER BATCH ===")

    # 1️⃣ Fetch raw data
    raw_data, source_name = fetch_arlamow()

    # 2️⃣ Normalize
    normalized = normalize_conditions(
        raw=raw_data,
        source=source_name
    )

    # 3️⃣ Blob connection
    conn_str = os.environ.get("BLOB_CONNECTION_STRING")
    if not conn_str:
        raise ValueError("BLOB_CONNECTION_STRING not set")

    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container_name = "data"

    blob_client = blob_service.get_blob_client(
        container=container_name,
        blob="conditions.json"
    )

    # 4️⃣ Final payload (na razie tylko Arłamów)
    payload = {
        "arlamow": normalized,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }

    blob_client.upload_blob(
        json.dumps(payload, ensure_ascii=False, indent=2),
        overwrite=True
    )

    print("=== SCRAPER FINISHED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
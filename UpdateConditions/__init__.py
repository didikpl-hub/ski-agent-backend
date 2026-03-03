import azure.functions as func
import logging
import json
import os
from azure.storage.blob import BlobServiceClient

from shared.sources import fetch_conditions_for_resort
from shared.normalize import normalize_conditions


def load_blob_json(blob_service_client, container, blob_name):
    blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
    data = blob_client.download_blob().readall()
    return json.loads(data)


def upload_blob_json(blob_service_client, container, blob_name, data):
    blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
    blob_client.upload_blob(
        json.dumps(data, ensure_ascii=False, indent=2),
        overwrite=True
    )


def main(mytimer: func.TimerRequest) -> None:
    logging.info("UpdateConditions function started.")

    try:
        # =====================
        # 1. Blob connection
        # =====================
        conn_str = os.environ.get("BLOB_CONNECTION_STRING")
        if not conn_str:
            logging.error("BLOB_CONNECTION_STRING not found")
            return

        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_name = "data"

        # =====================
        # 2. Load resorts
        # =====================
        resorts_data = load_blob_json(blob_service_client, container_name, "resorts.json")
        resorts = resorts_data.get("ski_resorts", [])

        conditions_output = {}

        # =====================
        # 3. Fetch + normalize
        # =====================
        for resort in resorts:
            try:
                resort_id = resort.get("id")
                if not resort_id:
                    continue

                raw_data, source = fetch_conditions_for_resort(resort)

                normalized = normalize_conditions(
                    raw=raw_data,
                    resort=resort,
                    source=source
                )

                conditions_output[resort_id] = normalized

            except Exception as e:
                logging.error(f"Error processing resort {resort.get('id')}: {str(e)}")
                continue

        # =====================
        # 4. Save conditions.json
        # =====================
        upload_blob_json(
            blob_service_client,
            container_name,
            "conditions.json",
            conditions_output
        )

        logging.info("UpdateConditions completed successfully.")

    except Exception as e:
        logging.error(f"UpdateConditions failed: {str(e)}")
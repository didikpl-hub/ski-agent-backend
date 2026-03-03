import azure.functions as func
import json
import os
from math import radians, sin, cos, sqrt, atan2
from azure.storage.blob import BlobServiceClient


# =========================
# Distance calculation
# =========================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


# =========================
# Blob loader
# =========================
def load_blob_json(blob_service_client, container, blob_name):
    blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
    try:
        data = blob_client.download_blob().readall()
        return json.loads(data)
    except Exception:
        return {}


# =========================
# Main function
# =========================
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # ---------------------
        # 1. GET params
        # ---------------------
        lat = float(req.params.get("lat", "52.2297"))
        lon = float(req.params.get("lon", "21.0122"))
        max_dist = float(req.params.get("dist_km", "200"))

        # ---------------------
        # 2. Blob connection
        # ---------------------
        conn_str = os.environ.get("BLOB_CONNECTION_STRING")
        if not conn_str:
            return func.HttpResponse(
                json.dumps({"error": "BLOB_CONNECTION_STRING not found"}),
                mimetype="application/json",
                status_code=500
            )

        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_name = "data"

        # ---------------------
        # 3. Load data
        # ---------------------
        resorts_data = load_blob_json(blob_service_client, container_name, "resorts.json")
        conditions_data = load_blob_json(blob_service_client, container_name, "conditions.json")

        resorts = resorts_data.get("ski_resorts", [])

        results = []

        # ---------------------
        # 4. Merge + compute
        # ---------------------
        for r in resorts:
            try:
                r_lat = r["location"]["lat"]
                r_lon = r["location"]["lon"]

                dist = haversine(lat, lon, r_lat, r_lon)

                if dist > max_dist:
                    continue

                resort_id = r["id"]
                conditions = conditions_data.get(resort_id, {})

                # ---------- STATIC ----------
                slopes_static = r.get("slopes", {})
                lifts_static = r.get("lifts", {})

                total_km = slopes_static.get("total_km")

                total_lifts = sum(
                    v for v in lifts_static.values()
                    if isinstance(v, (int, float))
                )

                # ---------- DYNAMIC ----------
                open_slopes = conditions.get("open_slopes") or {}

                green = open_slopes.get("green_km")
                blue = open_slopes.get("blue_km")
                red = open_slopes.get("red_km")
                black = open_slopes.get("black_km")

                open_values = [
                    v for v in [green, blue, red, black]
                    if isinstance(v, (int, float))
                ]

                open_total_km = round(sum(open_values), 2) if open_values else None

                percent_open = None
                if (
                    isinstance(open_total_km, (int, float)) and
                    isinstance(total_km, (int, float)) and
                    total_km > 0
                ):
                    percent_open = round(open_total_km / total_km, 2)

                # ---------- LIFTS SAFE GUARD ----------
                open_lifts_raw = conditions.get("open_lifts")

                if (
                    isinstance(open_lifts_raw, (int, float)) and
                    isinstance(total_lifts, (int, float))
                ):
                    open_lifts = min(open_lifts_raw, total_lifts)
                else:
                    open_lifts = open_lifts_raw

                # ---------- BUILD RESPONSE ----------
                merged = {
                    "id": resort_id,
                    "name": r.get("name"),
                    "region": r.get("region"),
                    "distance_km": round(dist, 1),

                    # status
                    "status": conditions.get("status"),

                    # snow
                    "snow_depth_cm": conditions.get("snow_depth_cm"),

                    # weather
                    "temperature_c": conditions.get("weather", {}).get("temperature_c"),

                    # slopes
                    "open_slopes": {
                        "green_km": green,
                        "blue_km": blue,
                        "red_km": red,
                        "black_km": black
                    },
                    "open_total_km": open_total_km,
                    "total_km": total_km,
                    "percent_open": percent_open,

                    # lifts
                    "open_lifts": open_lifts,
                    "total_lifts": total_lifts,

                    # meta
                    "updated_at": conditions.get("updated_at"),
                }

                results.append(merged)

            except Exception:
                continue

        # sort by distance
        results_sorted = sorted(results, key=lambda x: x["distance_km"])

        return func.HttpResponse(
            json.dumps(results_sorted, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
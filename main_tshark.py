import argparse
import json
import logging
import os
import sys
import threading
import time
from time import sleep

import requests
import uvicorn
import yaml

from src.router import ApiRouter
from src.subscription_registry import SubscriptionRegistry

logger = logging.getLogger("Packet capture producer")
logging.basicConfig(level=logging.DEBUG)

FIELDS_FILE = os.getenv("FIELDS_FILE", "fields.yml")
PRODUCER_ID = os.getenv("PRODUCER_ID", "packet-capture")


def try_numeric(value: str) -> int | float | str:
    """Convert string to int, float, or keep as string."""
    if isinstance(value, (int, float)):
        return value
    if not isinstance(value, str):
        return str(value)

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    # Keep as string
    return value


def flatten(layers: dict, allowed_fields: set | None = None) -> dict:

    def _flatten_intern(obj: dict, result: dict | None = None) -> dict:
        if result is None:
            result = {}
        for key, value in obj.items():
            if isinstance(value, dict):
                _flatten_intern(value, result)
            elif isinstance(value, list):
                continue
            elif allowed_fields is None or key in allowed_fields:
                clean_key = key.replace(".", "_")

                prefix = clean_key.split("_")[0]
                if clean_key.startswith(prefix + "_" + prefix + "_"):
                    clean_key = clean_key[len(prefix) + 1 :]

                result[clean_key] = try_numeric(value)

        return result

    return _flatten_intern(layers)


def aggregate_batch(batch: list) -> list:
    """Aggregate packet records by (ip_src, ip_dst), averaging all numeric fields per group."""
    if len(batch) <= 1:
        return batch

    groups: dict[tuple, dict] = {}  # (ip_src, ip_dst) -> {field: [values]}

    for record in batch:
        key = (record.get("ip_src", ""), record.get("ip_dst", ""))
        if key not in groups:
            groups[key] = {"_first": record, "_sums": {}, "_counts": {}}
        sums = groups[key]["_sums"]
        counts = groups[key]["_counts"]
        for field, val in record.items():
            if isinstance(val, (int, float)):
                sums[field] = sums.get(field, 0.0) + val
                counts[field] = counts.get(field, 0) + 1

    results = []
    for group in groups.values():
        first = group["_first"]
        sums = group["_sums"]
        counts = group["_counts"]
        record = {k: v for k, v in first.items() if not isinstance(v, (int, float))}
        for field in sums:
            record[field] = sums[field] / counts[field]
        results.append(record)

    return results


def send_batch(
    batch: list,
    subscription_registry: SubscriptionRegistry,
    producer_id: str,
    event_id: str,
):

    if not batch:
        return

    payload = {
        "analyticsData": [
            {
                "analyticsMetadata": record,
                "timestamp": int(time.time())
            }
            for record in batch
        ],
        "producerId": producer_id,
        "eventId": event_id,
    }

    for subscription_id in subscription_registry.all_subscribers():
        payload["subscription_id"] = subscription_id
        try:
            response = requests.post(
                subscription_registry.get_url(subscription_id), json=payload, timeout=5
            )
            response.raise_for_status()
            subscription_registry.record_success(subscription_id)
            print(f"Sent batch of {len(payload['analyticsData'])} lines successfully")
        except requests.RequestException as e:
            print(f"Error sending batch to API: {e}")
            subscription_registry.record_failure(subscription_id)


def _sender_loop(
    batch_lock: threading.Lock,
    batch_ref: list,
    subscription_registry: SubscriptionRegistry,
    event_id: str,
    send_after: float,
    stop_event: threading.Event,
):
    """Periodically flush the shared batch on a fixed timer, independent of stdin."""
    while not stop_event.is_set():
        sleep(send_after)
        with batch_lock:
            to_send = list(batch_ref)
            batch_ref.clear()
        send_batch(aggregate_batch(to_send), subscription_registry, PRODUCER_ID, event_id)


def main(
    cell_index: int,
    event_id: str,
    interval: float,
    send_after: float,
    no_filter: bool,
    port: int,
    host : str
):

    subscription_registry = SubscriptionRegistry()
    api = ApiRouter(subscription_registry, host, port)

    api_thread = threading.Thread(target=start_api, args=[api, port])
    api_thread.start()

    batch: list = []
    batch_lock = threading.Lock()
    stop_event = threading.Event()

    allowed_fields = None
    if not no_filter:
        if not os.path.isfile(FIELDS_FILE):
            logger.error(f"[{FIELDS_FILE}] not found. Please provide one")
            exit(1)
        with open(FIELDS_FILE) as f:
            allowed_fields = set(yaml.safe_load(f))

    sender_thread = threading.Thread(
        target=_sender_loop,
        args=(batch_lock, batch, subscription_registry, event_id, send_after, stop_event),
        daemon=True,
    )
    sender_thread.start()

    # Read tshark JSON lines from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        data: dict
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            logger.warning(f"Failled to convert line to json: {line}")
            continue

        if not data.get("layers", False):
            continue

        record = flatten(data["layers"], allowed_fields)
        ip_src = record.get("ip_src", "")
        if isinstance(ip_src, str) and ip_src.startswith("172.19.0.") and int(ip_src.split(".")[-1]) < 3:
            continue
        record["cell_index"] = cell_index
        record["timestamp"] = time.time()
        with batch_lock:
            batch.append(record)

        if interval:
            sleep(interval)

    # Send remaining
    stop_event.set()
    with batch_lock:
        remaining = list(batch)
        batch.clear()
    if remaining:
        send_batch(remaining, subscription_registry, PRODUCER_ID, event_id)


def start_api(api: ApiRouter, port: int):
    api.create_routes()
    uvicorn.run(api.app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send network capture to API with interval"
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Interval between sending lines (seconds)",
    )
    parser.add_argument(
        "-c",
        "--cell-index",
        type=int,
        default=1,
        help="Cell index to be added on POST ( for compability with the existing backend) ",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        default=False,
        help="Disable packet filter",
    )
    parser.add_argument(
        "-s", "--send", type=float, default=5, help="Interval between batch sends"
    )
    parser.add_argument(
        "-y", "--type", type=str, default="network_trafic", help="Data type"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=int(os.getenv("PORT", 8000)),
        help="Port of subscription api",
    )

    parser.add_argument(
        "-ho",
        "--host",
        type=str,
        default=(os.getenv("HOST", "producer-csv")),
        help="Host of producer api"
    )



    args = parser.parse_args()
    main(
        args.cell_index, args.type, args.interval, args.send, args.no_filter, args.port, args.host
    )

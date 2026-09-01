"""CSV export helper. Each router endpoint fetches its own filtered,
unpaginated rows (reusing the same repository filter builders as the
live list endpoints) and passes them here for serialization.
"""
import csv
import io
from typing import Any


def rows_to_csv(rows: list[dict[str, Any]], columns: list[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        flat = dict(row)
        if isinstance(flat.get("address"), dict):
            addr = flat["address"]
            flat["address"] = f"{addr.get('line1', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip', '')}"
        writer.writerow(flat)
    return buffer.getvalue()

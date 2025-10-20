import csv
import datetime as dt
import json
import os
from typing import List, Dict, Any

from .config import AppConfig


def _read_csv_rows(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not os.path.exists(path):
        return rows
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        all_rows = [r for r in reader if any(cell.strip() for cell in r)]
        if not all_rows:
            return rows
        headers = [h.strip() for h in all_rows[0]]
        for r in all_rows[1:]:
            if len(r) < len(headers):
                r += [""] * (len(headers) - len(r))
            rows.append(dict(zip(headers, r)))
    return rows


def _map_row_to_property(raw: Dict[str, str], idx: int) -> Dict[str, Any]:
    full_address = raw.get("Property Address", raw.get("Address", "")).strip()
    trademe_url = raw.get("Property Link", raw.get("TradeMe URL", "")).strip()
    asking_price = raw.get("Price", "").replace("Asking $", "").replace("$", "").replace(",", "").strip()
    try:
        asking_price_num = float(asking_price) if asking_price else 0
    except:
        asking_price_num = 0

    return {
        "id": idx,
        "address": full_address,
        "suburb": (full_address.split(",")[-1].strip() if "," in full_address else ""),
        "bedrooms": raw.get("Bedrooms", ""),
        "bathrooms": raw.get("Bathrooms", ""),
        "floor_area": raw.get("Area", "").replace(" m2", "").replace("m2", "").strip(),
        "asking_price": asking_price_num,
        "sale_method": raw.get("Open Home Status", ""),
        "trademe_url": trademe_url,
        "raw_data": raw,
    }


def run_batch(cfg: AppConfig, csv_paths: List[str]) -> Dict[str, Any]:
    """Run a batch analysis and return a results dict.

    Note: We reuse the analysis pipeline via app modules. Imports are placed
    here to avoid import cycles when packaging.
    """
    # Lazy imports from existing app
    from app.pipeline import process_addresses_with_urls

    all_properties: List[Dict[str, Any]] = []
    for path in csv_paths:
        for idx, row in enumerate(_read_csv_rows(path), 1):
            all_properties.append(_map_row_to_property(row, idx))

    # Prepare addresses for pipeline
    addresses = []
    for p in all_properties:
        addresses.append({"address": p.get("address", ""), "trademe_url": p.get("trademe_url", "")})

    # Call existing async pipeline
    import asyncio

    async def _analyze():
        return await process_addresses_with_urls(addresses)

    results = asyncio.run(_analyze())

    # Shape results similar to API output for downstream PDF/email
    shaped: List[Dict[str, Any]] = []
    for i, r in enumerate(results):
        shaped.append({
            "property": all_properties[i] if i < len(all_properties) else {"address": r.address},
            "analysis": {
                "score": r.score,
                "notes": r.notes,
                "scoring_breakdown": (r.scoring_breakdown.dict() if getattr(r, "scoring_breakdown", None) else None),
                "connection_data": (r.connection_data.dict() if getattr(r, "connection_data", None) else None),
            }
        })

    return {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "count": len(shaped),
        "results": shaped,
    }


def write_json(output_dir: str, payload: Dict[str, Any]) -> str:
    os.makedirs(output_dir, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"Results_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path



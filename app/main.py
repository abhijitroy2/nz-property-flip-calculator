from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import csv, io
from datetime import datetime, date, timedelta
import os
import re
import time

app = FastAPI(title="CSV Preview App")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/preview")
async def preview(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".csv", ".txt")):
        return JSONResponse(status_code=400, content={"error": "Only CSV or TXT files supported"})

    content = await file.read()
    try:
        buf = io.StringIO(content.decode("utf-8", errors="ignore"))
        reader = csv.reader(buf)
        rows = list(reader)
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Failed to parse CSV/TXT"})

    if not rows:
        return {"headers": [], "rows": []}

    raw_headers = [h.strip() for h in rows[0]]

    def normalize(name: str) -> str:
        return "".join(ch for ch in name.lower() if ch.isalnum())

    header_map = {normalize(h): idx for idx, h in enumerate(raw_headers)}
    addr_idx = header_map.get("propertyaddress", 0 if raw_headers else None)
    list_idx = header_map.get("listingdate", 1 if len(raw_headers) > 1 else None)

    def parse_listing_date(value: str):
        if not value:
            return None
        raw = value.strip()
        lower = raw.lower()

        # Remove optional leading label like "listed"
        if lower.startswith("listed "):
            lower = lower[len("listed "):]
            raw = raw[len("Listed "):] if raw.startswith("Listed ") else raw.split(" ", 1)[1]

        today_local = date.today()

        # Relative day terms
        if lower == "today":
            return today_local
        if lower == "yesterday":
            return today_local - timedelta(days=1)

        # "x days ago"
        import re
        m = re.match(r"^(\d{1,3})\s+days?\s+ago$", lower)
        if m:
            days = int(m.group(1))
            return today_local - timedelta(days=days)

        # Formats like "Thu, 2 Oct" or "2 Oct" (assume current year)
        month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        def parse_day_month(s: str):
            s = s.strip().replace(",", " ")
            parts = [p for p in s.split() if p]
            # Remove leading weekday if present
            if parts and parts[0][:3].lower() in ["mon","tue","wed","thu","fri","sat","sun"]:
                parts = parts[1:]
            if len(parts) >= 2:
                try:
                    day = int(parts[0])
                    mon_key = parts[1].lower()
                    if mon_key in month_map:
                        month = month_map[mon_key]
                        return date(today_local.year, month, day)
                except Exception:
                    return None
            return None

        dm = parse_day_month(raw)
        if dm:
            return dm

        # Try common absolute formats
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d %b %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%B %d, %Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).date()
            except Exception:
                continue
        # Last resort: ISO parser
        try:
            return date.fromisoformat(raw)
        except Exception:
            return None

    # We will return all original headers and insert derived columns:
    # 1) PotentialValue before PropertyLink
    # 2) Days on Market / Forced Sale columns after Listing Date (or at start if no Listing Date)
    output_headers = list(raw_headers)
    prop_link_raw_idx = header_map.get("propertylink")
    list_idx_raw = list_idx

    pv_insert_pos = prop_link_raw_idx if (prop_link_raw_idx is not None and prop_link_raw_idx <= len(output_headers)) else len(output_headers)
    output_headers.insert(pv_insert_pos, "PotentialValue")

    # Adjust derived insert position if PotentialValue was inserted before it
    insert_pos = (list_idx_raw + 1) if (list_idx_raw is not None and list_idx_raw < len(raw_headers)) else 0
    if pv_insert_pos <= insert_pos:
        insert_pos += 1
    for label in ["Days on Market", "Forced Sale Likelihood", "Forced Sale Triggers", "Forced Sale Rationale"]:
        output_headers.insert(insert_pos, label)
        insert_pos += 1
    output_rows = []
    today = date.today()

    # Locate optional indices used for enrichment/sorting
    title_idx = header_map.get("propertytitle")
    area_idx = header_map.get("area")
    prop_link_idx = prop_link_raw_idx

    very_strong_patterns = [
        r"\bmortgagee\b",
        r"\bmortgage(s|e)?\b",
        r"\bdeceased estate\b",
        r"\bmust\s+sell\b",
        r"\bno\s+plan\s*b\b",
        r"\burgent(\s+sale)?\b",
        r"\bas[-\s]?is(\s*\/\s*where[-\s]?is)?\b",
        r"\bfire\s+sale\b",
    ]
    medium_patterns = [
        r"\bvendor\s+relocated\b",
        r"\bvendor\s+committed\b",
        r"\bfinal\s+call\b",
        r"\blast\s+chance\b",
        r"\bpriced\s+to\s+sell\b",
        r"\bmust\s+be\s+sold\b",
        r"\bmotivated\s+vendor\b",
        r"\bno\s+plan\s*b\b",
    ]
    weak_patterns = [
        r"\bopportunity\b",
        r"\binvestors?\b",
        r"\baffordable\b",
        r"\bbrand\s+new\b",
        r"\bpriced\s+to\s+sell\b",
    ]

    def analyze_forced_sale(title: str):
        if not title:
            return 0.0, [], ""
        text = title.lower()
        matches = []
        score = 0.0
        # Collect matches per tier
        tier = None
        for pat in very_strong_patterns:
            m = re.search(pat, text)
            if m:
                matches.append(m.group(0))
                score = max(score, 1.0)
                tier = "very strong"
        if score < 1.0:
            for pat in medium_patterns:
                m = re.search(pat, text)
                if m:
                    matches.append(m.group(0))
                    score = max(score, 0.6)
                    if not tier:
                        tier = "medium"
        if score < 0.6:
            for pat in weak_patterns:
                m = re.search(pat, text)
                if m:
                    matches.append(m.group(0))
                    score = max(score, 0.2)
                    if not tier:
                        tier = "weak"
        rationale = "" if not matches else f"Signals: {', '.join(sorted(set(matches)))} ({tier})"
        return round(score, 2), matches, rationale
    def parse_area(value: str) -> float:
        if not value:
            return 0.0
        txt = value.lower().replace(",", " ")
        # extract first number (int or float)
        m = re.search(r"(\d+(?:\.\d+)?)", txt)
        return float(m.group(1)) if m else 0.0

    # Selenium setup (only if at least one PropertyLink exists)
    def make_driver():
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
        except Exception:
            return None
        options = ChromeOptions()
        headless_env = os.getenv("HEADLESS", "true").lower()
        headless = headless_env not in ("0", "false", "no")
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1280,2000")
        service = ChromeService(ChromeDriverManager().install())
        try:
            return webdriver.Chrome(service=service, options=options)
        except Exception:
            return None

    def extract_potential_value_from_html(html: str) -> str:
        if not html:
            return ""
        anchor_words = ["homesestimate", "homes estimate", "estimate", "valuation", "value"]
        lower_html = html.lower()
        # Find nearest anchor occurrence
        pos = -1
        for word in anchor_words:
            pos = lower_html.find(word)
            if pos != -1:
                break
        # Search within a window for dollar amounts
        if pos == -1:
            window = html
        else:
            start = max(0, pos - 4000)
            end = min(len(html), pos + 8000)
            window = html[start:end]
        m = re.search(r"\$\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]{1,2})?", window)
        return m.group(0) if m else ""

    def fetch_potential_value(driver, url: str) -> str:
        if not driver or not url:
            return ""
        try:
            driver.get(url)
            time.sleep(1.2)
            # Gradual scroll to trigger lazy sections
            total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
            y = 0
            step = 700
            deadline = time.monotonic() + float(os.getenv("PV_PER_URL_TIMEOUT_SECS", "10"))
            for _ in range(12):
                driver.execute_script(f"window.scrollTo(0, {y});")
                time.sleep(0.35)
                html = driver.page_source
                val = extract_potential_value_from_html(html)
                if val:
                    return val
                y += step
                if y >= total_height:
                    break
                if time.monotonic() > deadline:
                    break
            # Final attempt
            return extract_potential_value_from_html(driver.page_source)
        except Exception:
            return ""

    enriched_rows = []
    need_driver = any((len(r) > prop_link_idx and r[prop_link_idx]) for r in rows[1:]) if prop_link_idx is not None else False
    driver = make_driver() if need_driver else None
    for r in rows[1:]:
        # Normalize row length to headers
        current = list(r) + [""] * max(0, len(raw_headers) - len(r))

        listing_raw = (current[list_idx].strip() if list_idx is not None and list_idx < len(current) else "")
        listing_dt = parse_listing_date(listing_raw)
        dom_val = (today - listing_dt).days if listing_dt else 0

        fs_score, fs_triggers, fs_rationale = analyze_forced_sale(
            current[title_idx].strip() if title_idx is not None and title_idx < len(current) else ""
        )

        area_val = parse_area(current[area_idx]) if area_idx is not None and area_idx < len(current) else 0.0
        # PotentialValue via PropertyLink
        potential_value = ""
        if prop_link_idx is not None and prop_link_idx < len(current):
            url = (current[prop_link_idx] or "").strip()
            if url and driver:
                potential_value = fetch_potential_value(driver, url)
                time.sleep(1.0)  # small delay to be gentle

        # Build output row: start with original columns
        out_row = [*current[:len(raw_headers)]]
        # Insert PotentialValue before PropertyLink
        pv_at = prop_link_raw_idx if (prop_link_raw_idx is not None and prop_link_raw_idx <= len(raw_headers)) else len(out_row)
        out_row.insert(pv_at, potential_value)
        # Insert derived values at the same position used for headers, accounting for PV if inserted before
        insert_at = (list_idx + 1) if (list_idx is not None and list_idx < len(raw_headers)) else 0
        if pv_at <= insert_at:
            insert_at += 1
        derived_values = [dom_val, f"{fs_score}", ", ".join(sorted(set(fs_triggers))) if fs_triggers else "", fs_rationale]
        for offset, val in enumerate(derived_values):
            out_row.insert(insert_at + offset, val)

        enriched_rows.append((out_row, dom_val, fs_score, area_val))

    # Sort by: Days on Market desc, Forced Sale Likelihood desc, Area desc
    enriched_rows.sort(key=lambda t: (t[1], t[2], t[3]), reverse=True)

    output_rows = [t[0] for t in enriched_rows]

    if driver:
        try:
            driver.quit()
        except Exception:
            pass

    return {"headers": output_headers, "rows": output_rows}
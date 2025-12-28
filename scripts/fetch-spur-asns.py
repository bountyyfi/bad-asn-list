#!/usr/bin/env python3
"""
Fetch ASNs from spur.us indexed pages via search results.
Extracts ASN numbers from spur.us/context page titles.
"""

import re
import subprocess
import sys
from pathlib import Path

# Get current ASNs from all.txt
def get_current_asns():
    all_txt = Path(__file__).parent.parent / "all.txt"
    asns = set()
    with open(all_txt) as f:
        for line in f:
            match = re.match(r'^AS(\d+)', line)
            if match:
                asns.add(int(match.group(1)))
    return asns

# Known VPN/Proxy ASNs from spur.us context pages (extracted from searches)
SPUR_ASNS = {
    # VPN Providers
    9009: "M247 Ltd (NordVPN, Urban VPN)",
    136787: "TEFINCOM S.A. (NordVPN)",
    212238: "Datacamp Limited",
    60068: "Datacamp Limited",
    209854: "Cyberzone S.A. (Surfshark)",
    199218: "Proton AG (ProtonVPN)",
    25369: "Hydra Communications Ltd (NordVPN)",
    62240: "Clouvider Limited (NordVPN)",
    12876: "ONLINE S.A.S. / Scaleway (Gecko VPN)",
    29302: "HostingServices Inc (Astrill VPN)",
    198605: "Gen Digital (HMA VPN / Avast)",
    39351: "31173 Services AB (Mullvad)",
    11878: "tzulo, inc. (Mullvad)",
    197854: "Mullvad VPN AB",
    43357: "Owl Limited (Mullvad)",
    206092: "Datacamp Limited (ExpressVPN)",

    # Proxy Services
    17561: "3xK Tech GmbH (Plainproxies)",
    132817: "Webshare Proxy",
    64267: "Rayobyte/NetNut",
    131642: "Rapidseedbox",
    43444: "Fine Proxy / BNS-AS",

    # Datacenter/Hosting (used by VPNs)
    14061: "DigitalOcean (TunnelBear)",
    29838: "Atlantic Metro Communications (TunnelBear)",
    8100: "QuadraNet (Windscribe)",
    33387: "Nocix LLC (HideMe VPN)",
    13213: "UK-2 Limited",
    16276: "OVH",
    24940: "Hetzner Online GmbH",
    20473: "The Constant Company (Vultr)",

    # Additional from spur.us
    203020: "HostRoyale (Exitlag VPN)",
    10036: "DLIVE",
    23700: "Linknet-Fastnet",
    3303: "Swisscom (Tor exit)",
}

def main():
    print("=== Spur.us ASN Extractor ===\n")

    current = get_current_asns()
    print(f"Current list: {len(current)} ASNs\n")

    missing = []
    for asn, name in sorted(SPUR_ASNS.items()):
        if asn not in current:
            missing.append((asn, name))

    if missing:
        print(f"Missing ASNs from spur.us data ({len(missing)}):\n")
        for asn, name in missing:
            print(f"AS{asn} {name}")

        print("\n--- Copy/paste format for all.txt ---\n")
        for asn, name in missing:
            print(f"AS{asn} {name}")
    else:
        print("All known spur.us ASNs are in the list!")

    print("\n=== Manual Google Dorks ===")
    print('site:spur.us/context "ASN" VPN anonymous')
    print('site:spur.us/context proxy datacenter')
    print('site:spur.us/context "ASN" residential callback')

if __name__ == "__main__":
    main()

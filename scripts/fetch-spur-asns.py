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
# Updated 2025-12-28 with comprehensive VPN provider list
SPUR_ASNS = {
    # === Major VPN Providers ===
    9009: "M247 Ltd (NordVPN, Urban VPN, Touch VPN, Snap VPN)",
    136787: "TEFINCOM S.A. (NordVPN)",
    207137: "Owl Limited (NordVPN)",
    25369: "Hydra Communications Ltd (NordVPN)",
    62240: "Clouvider Limited (NordVPN, ExpressVPN)",
    209854: "Cyberzone S.A. (Surfshark)",
    199218: "Proton AG (ProtonVPN)",
    212238: "Datacamp Limited (ProtonVPN, PrivateVPN)",
    60068: "Datacamp Limited (ProtonVPN)",
    49981: "WorldStream B.V. (ProtonVPN)",
    206092: "Datacamp Limited (ExpressVPN)",
    42831: "UK-2 Limited (ExpressVPN)",
    29066: "VELCOM (ExpressVPN)",
    39351: "31173 Services AB (Mullvad)",
    11878: "tzulo, inc. (Mullvad)",
    197854: "Mullvad VPN AB",
    43357: "Owl Limited (Mullvad)",
    198605: "Gen Digital (HMA VPN / Avast)",

    # === Secondary VPN Providers ===
    12876: "ONLINE S.A.S. / Scaleway (Gecko VPN, Veepn)",
    29302: "HostingServices Inc (Astrill VPN)",
    46475: "Limestone Networks (TunnelBear)",
    29838: "Atlantic Metro Communications (TunnelBear)",
    8100: "QuadraNet (Windscribe)",
    33387: "Nocix LLC (hide.me VPN)",
    203020: "HostRoyale (Exitlag VPN)",
    202422: "G-Core Labs S.A. (iTop VPN, VPN Super)",
    53667: "PONYNET (Thunder VPN)",
    21859: "Zenlayer Inc (Snap VPN)",
    62756: "GTHost (Melon VPN, VPN Super)",

    # === CyberGhost/Zenmate Network ===
    174: "Cogent (CyberGhost, Zenmate) - major backbone, use carefully",
    30633: "Leaseweb USA (CyberGhost)",

    # === Privacy VPNs ===
    # Perfect Privacy, Browsec, VyprVPN infrastructure
    19148: "Golden Frog (VyprVPN)",

    # === Free/Budget VPNs ===
    # Hola, Thunder VPN, UFO VPN, Panda VPN, etc.
    # These typically use major cloud providers

    # === Proxy Services ===
    17561: "3xK Tech GmbH (Plainproxies)",
    132817: "Webshare Proxy",
    64267: "Rayobyte/NetNut",
    131642: "Rapidseedbox",
    43444: "Fine Proxy / BNS-AS",
    50304: "Cohesity (Webshare Proxy)",

    # === Datacenter/Hosting (heavy VPN usage) ===
    14061: "DigitalOcean (TunnelBear, Speedify, Hola, Xvpn)",
    16276: "OVH (Veepn, Xvpn, CyberGhost, Hola)",
    24940: "Hetzner Online GmbH",
    20473: "The Constant Company / Vultr (TunnelBear)",
    63949: "Akamai / Linode (Speedify)",
    13213: "UK-2 Limited",
    36352: "ColoCrossing (Mysterium VPN)",

    # === Bulletproof/Stark Industries Network ===
    44477: "PQ Hosting Plus S.R.L. (Stark Industries)",
    209847: "WorkTitans B.V. (Stark Industries successor)",
    210644: "AEZA INTERNATIONAL LTD (Lantern VPN, Tor)",

    # === Consumer ISPs (skip these) ===
    # 3303: "Swisscom (Tor exit)" - consumer ISP, don't block
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

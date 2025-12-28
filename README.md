# Bad ASN List

A curated blocklist of Autonomous System Numbers (ASNs) associated with VPN providers, datacenters, and hosting services commonly used for malicious traffic, scraping, and automated abuse.

## Purpose

This list helps protect web applications and APIs from:
- Automated scanning and scraping
- Credential stuffing attacks
- Bot traffic from datacenter IPs
- Anonymous abuse via commercial VPNs

## Categories

| Category | Examples |
|----------|----------|
| **VPN Providers** | NordVPN, ExpressVPN, Surfshark, ProtonVPN, Mullvad, PIA, IPVanish, Windscribe, AzireVPN, PrivateVPN, VyprVPN, Freedome, Speedify, Browsec, HMA, Hotspot Shield |
| **Major Hosting** | Hetzner, Vultr, DigitalOcean, Linode, OVH, Leaseweb |
| **Budget Hosting** | BuyVM, Hostinger, ColoCrossing, Contabo |
| **Chinese Cloud** | Alibaba Cloud, Tencent Cloud, Huawei Cloud, Baidu Cloud |
| **Eastern EU/RU** | PQ Hosting, Selectel, Hostry, AEZA, FairyHosting, ESTOXY, VEESP, Yuroit |
| **Attack Sources** | H2NEXUS, Quality Network, FORTIS-AS, BNS-AS, GIGAHOST, R0CKET-CLOUD |
| **Bulletproof Hosting** | Proton66, PROSPERO, Chang Way, Qwins Ltd, NYBULA, CHEAPY-HOST, Media Land |
| **Ukraine/Seychelles BPH** | VAIZ-AS, FDN3, E-RISHENNYA, TK-NET, ROZA-AS, SS-Net, ELITETEAM/1337TEAM |
| **Stark Industries** | PQ Hosting, MIRhosting, WorkTitans |
| **CrazyRDP Network** | Delis LLC, EKABI, Zhongguancun, Limenet, Sovy Cloud |
| **FIN7/Ransomware** | SmartApe, Flyservers, Alviva |
| **Privacy Hosting** | IncogNET, Njalla |
| **Proxy Services** | CroxyProxy, MEVSPACE |
| **Scanners** | Censys, Shodan |

## Files

- `all.txt` - Complete list of 1000 blocked ASNs with organization names

## Usage

### Cloudflare Workers - Basic

```javascript
const BLOCKED_ASNS = new Set([
  9009, 136787, 212238, 60068, 174, 16276, 24940, 14061, 63949, 20473,
  // ... import full list from all.txt
]);

export default {
  async fetch(request) {
    const asn = request.cf?.asn;
    if (asn && BLOCKED_ASNS.has(asn)) {
      return new Response('Forbidden', { status: 403 });
    }
    return fetch(request);
  }
}
```

### Cloudflare Workers - With Logging

```javascript
const BLOCKED_ASNS = new Set([9009, 136787, 212238, 60068, /* ... */]);

export default {
  async fetch(request, env) {
    const cf = request.cf;
    const asn = cf?.asn;
    const org = cf?.asOrganization;

    if (asn && BLOCKED_ASNS.has(asn)) {
      console.log(`Blocked: ASN ${asn} (${org}) - ${request.url}`);
      return new Response('Forbidden', {
        status: 403,
        headers: { 'X-Blocked-ASN': String(asn) }
      });
    }
    return fetch(request);
  }
}
```

### Cloudflare Workers - Rate Limit Instead of Block

```javascript
const BLOCKED_ASNS = new Set([9009, 136787, 212238, 60068, /* ... */]);

export default {
  async fetch(request, env) {
    const asn = request.cf?.asn;

    if (asn && BLOCKED_ASNS.has(asn)) {
      // Rate limit suspicious ASNs via KV
      const key = `rate:${asn}:${new Date().getMinutes()}`;
      const count = parseInt(await env.KV.get(key) || '0');

      if (count > 100) {
        return new Response('Rate limited', { status: 429 });
      }
      await env.KV.put(key, String(count + 1), { expirationTtl: 120 });
    }
    return fetch(request);
  }
}
```

### Node.js / Express

```javascript
import fs from 'fs';

const blockedAsns = new Set(
  fs.readFileSync('all.txt', 'utf-8')
    .split('\n')
    .map(line => parseInt(line.match(/^AS(\d+)/)?.[1]))
    .filter(Boolean)
);

// With express + express-ip or similar
app.use((req, res, next) => {
  const asn = req.ip_info?.asn; // depends on your IP info provider
  if (asn && blockedAsns.has(asn)) {
    return res.status(403).send('Forbidden');
  }
  next();
});
```

### Python / Flask

```python
import re

with open('all.txt') as f:
    BLOCKED_ASNS = {
        int(m.group(1))
        for line in f
        if (m := re.match(r'^AS(\d+)', line))
    }

@app.before_request
def check_asn():
    asn = get_asn_from_ip(request.remote_addr)  # use ipinfo, maxmind, etc.
    if asn in BLOCKED_ASNS:
        abort(403)
```

### iptables / nftables

```bash
#!/bin/bash
# Requires: ipset, whois or bgpq4

# Create ipset
ipset create bad-asns hash:net

# Fetch prefixes for each ASN and add to ipset
while read -r line; do
  asn=$(echo "$line" | grep -oE '^AS[0-9]+')
  [ -z "$asn" ] && continue

  # Using bgpq4 (faster, recommended)
  bgpq4 -4 -l pfx "$asn" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+' | \
    while read prefix; do
      ipset add bad-asns "$prefix" 2>/dev/null
    done
done < all.txt

# Block with iptables
iptables -I INPUT -m set --match-set bad-asns src -j DROP
iptables -I FORWARD -m set --match-set bad-asns src -j DROP

# Or with nftables
# nft add set inet filter bad-asns { type ipv4_addr; flags interval; }
# nft add rule inet filter input ip saddr @bad-asns drop
```

### Parse the list

```bash
# Extract ASN numbers only
grep -oE '^AS[0-9]+' all.txt | sed 's/AS//'

# Generate JavaScript Set
echo "new Set([$(grep -oE '^AS[0-9]+' all.txt | sed 's/AS//' | tr '\n' ',' | sed 's/,$//')]);"

# Generate Python set
echo "{$(grep -oE '^AS[0-9]+' all.txt | sed 's/AS//' | tr '\n' ',' | sed 's/,$//')}"
```

## Contributing

Submit a PR to add missing ASNs. Include:
- ASN number
- Organization name
- Category (VPN/Hosting/Scanner/etc.)

## Related

- [Bountyy Oy](https://bountyy.fi) - Penetration testing & cybersecurity
- [Lonkero](https://lonkero.bountyy.fi/en) - Security scanner by Bountyy Oy

## License

MIT

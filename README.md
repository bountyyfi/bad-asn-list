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
| **VPN Providers** | NordVPN, ExpressVPN, Surfshark, ProtonVPN, Mullvad, PIA, IPVanish, Windscribe, AzireVPN, PrivateVPN, VyprVPN |
| **Major Hosting** | Hetzner, Vultr, DigitalOcean, Linode, OVH |
| **Budget Hosting** | BuyVM, Hostinger, ColoCrossing, Contabo |
| **Eastern EU/RU** | PQ Hosting, Selectel, Hostry, AEZA, FairyHosting, ESTOXY |
| **Attack Sources** | H2NEXUS, Quality Network, FORTIS-AS, BNS-AS, GIGAHOST, R0CKET-CLOUD |
| **Scanners** | Censys, Shodan |

## Files

- `all.txt` - Complete list of 945 blocked ASNs with organization names

## Usage

### Cloudflare Workers

```javascript
const BLOCKED_ASNS = new Set([/* ASNs from all.txt */]);

export default {
  async fetch(request) {
    const asn = request.cf?.asn;
    if (BLOCKED_ASNS.has(asn)) {
      return new Response('Access denied', { status: 403 });
    }
    return fetch(request);
  }
}
```

### Parse the list

```bash
# Extract ASN numbers only
grep -oP 'AS\K[0-9]+' all.txt
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
